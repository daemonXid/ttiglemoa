from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Currency(models.TextChoices):
    KRW = "KRW", "원화(KRW)"
    USD = "USD", "달러(USD)"
    JPY = "JPY", "엔(JPY)"
    EUR = "EUR", "유로(EUR)"


class Compounding(models.TextChoices):
    NONE = "NONE", "미적용(단리)"
    MONTHLY = "MONTHLY", "월복리"
    QUARTERLY = "QUARTERLY", "분기복리"
    ANNUALLY = "ANNUALLY", "연복리"


class Market(models.TextChoices):
    KR = "KR", "국내"
    US = "US", "해외(미국)"


class DepositSaving(TimeStampedModel):
    class ProductType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "예금"
        SAVING = "SAVING", "적금"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposit_savings",
        verbose_name="사용자",
    )
    product_type = models.CharField(
        max_length=16, choices=ProductType.choices, verbose_name="유형"
    )
    bank_name = models.CharField(max_length=100, verbose_name="은행명")
    product_name = models.CharField(max_length=150, verbose_name="상품명")
    principal_amount = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name="원금"
    )
    annual_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="연이율(%) 예: 3.50",
        verbose_name="연이율(%)",
    )
    compounding = models.CharField(
        max_length=16, choices=Compounding.choices, default=Compounding.NONE, verbose_name="복리 주기"
    )
    start_date = models.DateField(verbose_name="시작일")
    maturity_date = models.DateField(null=True, blank=True, verbose_name="만기일")
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="통화"
    )

    # 사용자가 직접 입력하는 현재 평가액(선택)
    current_value_manual = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="평가액(직접입력)"
    )

    def __str__(self):
        return f"{self.bank_name} {self.product_name} ({self.product_type})"

    def estimated_value(self, as_of=None):
        """
        간단 계산: 단리 또는 단순 복리 근사로 현재 평가액 추정.
        current_value_manual 이 있으면 우선 사용.
        """
        if self.current_value_manual is not None:
            return self.current_value_manual

        as_of = as_of or timezone.localdate()
        end_date = min(as_of, self.maturity_date) if self.maturity_date else as_of
        days = (end_date - self.start_date).days
        if days <= 0:
            return self.principal_amount

        rate = float(self.annual_rate) / 100.0
        # 단리
        if self.compounding == Compounding.NONE:
            years = days / 365.0
            return self.principal_amount * (1 + rate * years)

        # 복리 근사
        if self.compounding == Compounding.MONTHLY:
            periods = max(0, int(days // 30))
            period_rate = rate / 12.0
        elif self.compounding == Compounding.QUARTERLY:
            periods = max(0, int(days // 91))
            period_rate = rate / 4.0
        else:  # ANNUALLY
            periods = max(0, int(days // 365))
            period_rate = rate

        value = float(self.principal_amount) * ((1 + period_rate) ** periods)
        return round(value, 2)

    def get_last_change(self):
        """최근 변동값과 변동률을 반환합니다."""
        delta, pct = deposit_last_change(self)
        return delta, pct


class StockHolding(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stock_holdings",
        verbose_name="사용자",
    )
    market = models.CharField(max_length=8, choices=Market.choices, verbose_name="시장")
    ticker = models.CharField(max_length=20, verbose_name="티커/종목코드")
    name = models.CharField(max_length=150, blank=True, verbose_name="종목명")
    quantity = models.DecimalField(max_digits=18, decimal_places=4, verbose_name="수량")
    average_price = models.DecimalField(
        max_digits=18, decimal_places=4, help_text="매수평균단가 (거래통화)", verbose_name="평단가"
    )
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="통화"
    )
    current_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True, help_text="현재가 (선택)", verbose_name="현재가"
    )
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.ticker} ({self.market})"

    def estimated_value(self):
        price = self.current_price if self.current_price is not None else self.average_price
        return price * self.quantity

    def purchase_value(self):
        """매수 총액 (평단가 * 수량)"""
        return self.average_price * self.quantity

    def get_last_change(self):
        """최근 변동값과 변동률을 반환합니다."""
        delta, pct = stock_last_change(self)
        return delta, pct

    def update_price_via_fdr(self):
        """FinanceDataReader로 최신 종가 조회 후 current_price 업데이트.
        시장 구분은 보조정보로 사용하며, FDR은 KR/US를 모두 지원.
        반환: 성공 여부(bool)
        """
        try:
            import FinanceDataReader as fdr
        except ImportError:
            return False

        try:
            df = fdr.DataReader(self.ticker)
            if df is None or df.empty:
                return False

            # 종가 컬럼 우선
            close = df["Close"].iloc[-1]
            self.current_price = close
            self.last_price_updated_at = timezone.now()
            self.save(update_fields=["current_price", "last_price_updated_at", "updated_at"])

            # 히스토리 저장
            try:
                StockPriceHistory.objects.create(
                    stock=self,
                    price=self.current_price,
                    recorded_at=self.last_price_updated_at,
                    source="FDR",
                )
            except Exception:
                pass
            return True
        except Exception:
            return False


class BondHolding(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bond_holdings",
        verbose_name="사용자",
    )
    name = models.CharField(max_length=150, verbose_name="채권명")
    issuer = models.CharField(max_length=150, blank=True, verbose_name="발행처")
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="통화"
    )
    face_amount = models.DecimalField(
        max_digits=18, decimal_places=2, help_text="액면총액", verbose_name="액면총액"
    )
    coupon_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="표면금리(%)", verbose_name="표면금리(%)"
    )
    purchase_price_pct = models.DecimalField(
        max_digits=6, decimal_places=3, help_text="매수가(액면가=100 기준)", verbose_name="매수가(%)"
    )
    current_price_pct = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True, help_text="현재가(선택)", verbose_name="현재가(%)"
    )
    maturity_date = models.DateField(verbose_name="만기일")
    bond_code = models.CharField(max_length=32, blank=True, help_text="KRX 채권 코드/ISIN (pykrx 조회용)", verbose_name="채권코드")
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.currency})"

    def estimated_value(self):
        price_pct = (
            self.current_price_pct if self.current_price_pct is not None else self.purchase_price_pct
        )
        return self.face_amount * (price_pct / 100)

    def get_last_change(self):
        """최근 변동값과 변동률을 반환합니다."""
        delta_pct, pct = bond_last_change(self)
        return delta_pct, pct

    def update_price_via_pykrx(self):
        """pykrx로 채권 현재가(%)를 업데이트. KRX 코드가 필요할 수 있음.
        구현은 가용 엔드포인트에 따라 단순화.
        반환: 성공 여부(bool)
        """
        try:
            from pykrx import bond
        except ImportError:
            return False

        code = self.bond_code or None
        if not code:
            return False

        try:
            # 일별 시세 DataFrame을 받아 마지막 값 사용
            today = timezone.localdate().strftime("%Y%m%d")
            try:
                df = bond.get_bond_ohlcv_by_date(today, today, code)
            except Exception:
                df = None

            if df is None or df.empty:
                return False

            # 종가 또는 평가가격에 해당하는 컬럼 추정
            for col in ["종가", "Close", "close", "수익률", "Price"]:
                if col in df.columns:
                    val = float(df[col].iloc[-1])
                    # % 기준 가격으로 가정
                    self.current_price_pct = val
                    self.last_price_updated_at = timezone.now()
                    self.save(update_fields=["current_price_pct", "last_price_updated_at", "updated_at"])

                    # 히스토리 저장
                    try:
                        BondPriceHistory.objects.create(
                            bond=self,
                            price_pct=self.current_price_pct,
                            recorded_at=self.last_price_updated_at,
                            source="pykrx",
                        )
                    except Exception:
                        pass
                    return True
            return False
        except Exception:
            return False


class StockPriceHistory(models.Model):
    stock = models.ForeignKey(StockHolding, on_delete=models.CASCADE, related_name="price_history")
    recorded_at = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=18, decimal_places=4)
    source = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["-recorded_at", "-id"]


class BondPriceHistory(models.Model):
    bond = models.ForeignKey(BondHolding, on_delete=models.CASCADE, related_name="price_history")
    recorded_at = models.DateTimeField(default=timezone.now)
    price_pct = models.DecimalField(max_digits=8, decimal_places=3)
    source = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["-recorded_at", "-id"]


class DepositValueHistory(models.Model):
    deposit = models.ForeignKey(DepositSaving, on_delete=models.CASCADE, related_name="value_history")
    recorded_at = models.DateTimeField(default=timezone.now)
    value = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        ordering = ["-recorded_at", "-id"]


# Convenience helpers to compute last change
def _last_change_from_history(values: list[float]):
    if len(values) < 2:
        return None, None
    prev = float(values[1])
    curr = float(values[0])
    delta = curr - prev
    pct = (delta / prev * 100.0) if prev != 0 else None
    return delta, (round(pct, 2) if pct is not None else None)


def _get_two_prices_qs(qs, field):
    qs = qs.values_list(field, flat=True)[:2]
    return list(qs)


def stock_last_change(stock: "StockHolding"):
    prices = _get_two_prices_qs(stock.price_history, "price")
    return _last_change_from_history(prices)


def bond_last_change(bond: "BondHolding"):
    prices = _get_two_prices_qs(bond.price_history, "price_pct")
    return _last_change_from_history(prices)


def deposit_last_change(deposit: "DepositSaving"):
    vals = _get_two_prices_qs(deposit.value_history, "value")
    return _last_change_from_history(vals)
