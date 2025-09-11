from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Currency(models.TextChoices):
    KRW = "KRW", "��ȭ(KRW)"
    USD = "USD", "�޷�(USD)"
    JPY = "JPY", "��(JPY)"
    EUR = "EUR", "����(EUR)"


class Compounding(models.TextChoices):
    NONE = "NONE", "�ܸ�"
    MONTHLY = "MONTHLY", "?�복�?
    QUARTERLY = "QUARTERLY", "분기복리"
    ANNUALLY = "ANNUALLY", "?�복�?


class Market(models.TextChoices):
    KR = "KR", "����"
    US = "US", "�ؿ�(�̱�)"


class DepositSaving(TimeStampedModel):
    class ProductType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "����"
        SAVING = "SAVING", "����"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposit_savings",
        verbose_name="?�용??,
    )
    product_type = models.CharField(
        max_length=16, choices=ProductType.choices, verbose_name="?�형"
    )
    bank_name = models.CharField(max_length=100, verbose_name="?�?�명")
    product_name = models.CharField(max_length=150, verbose_name="?�품�?)
    principal_amount = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name="?�금"
    )
    annual_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="?�이??%) ?? 3.50",
        verbose_name="?�이??%)",
    )
    compounding = models.CharField(
        max_length=16, choices=Compounding.choices, default=Compounding.NONE, verbose_name="복리 주기"
    )
    start_date = models.DateField(verbose_name="?�작??)
    maturity_date = models.DateField(null=True, blank=True, verbose_name="만기??)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="?�화"
    )

    # ?�용?��? 직접 ?�력?�는 ?�재 ?��????�택)
    current_value_manual = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="?��???직접?�력)"
    )

    def __str__(self):
        return f"{self.bank_name} {self.product_name} ({self.product_type})"

    def estimated_value(self, as_of=None):
        """
        간단 계산: ?�리 ?�는 ?�순 복리 근사�??�재 ?��???추정.
        current_value_manual ???�으�??�선 ?�용.
        """
        if self.current_value_manual is not None:
            return self.current_value_manual

        as_of = as_of or timezone.localdate()
        end_date = min(as_of, self.maturity_date) if self.maturity_date else as_of
        days = (end_date - self.start_date).days
        if days <= 0:
            return self.principal_amount

        rate = float(self.annual_rate) / 100.0
        # ?�리
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
        from .models import deposit_last_change  # local import to avoid cyc.
        delta, pct = deposit_last_change(self)
        return delta, pct


class StockHolding(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stock_holdings",
        verbose_name="?�용??,
    )
    market = models.CharField(max_length=8, choices=Market.choices, verbose_name="?�장")
    ticker = models.CharField(max_length=20, verbose_name="?�커/종목코드")
    name = models.CharField(max_length=150, blank=True, verbose_name="종목�?)
    quantity = models.DecimalField(max_digits=18, decimal_places=4, verbose_name="?�량")
    average_price = models.DecimalField(
        max_digits=18, decimal_places=4, help_text="매수?�균?��? (거래?�화)", verbose_name="?�단가"
    )
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="?�화"
    )
    current_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True, help_text="?�재가 (?�택)", verbose_name="?�재가"
    )
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.ticker} ({self.market})"

    def estimated_value(self):
        price = self.current_price if self.current_price is not None else self.average_price
        return price * self.quantity

    def update_price_via_fdr(self):
        """FinanceDataReader�?최신 종�? 조회 ??current_price ?�데?�트.
        ?�장 구분?� 보조?�보�??�용?�며, FDR?� KR/US�?모두 지??
        반환: ?�공 ?��?(bool)
        """
        try:
            import FinanceDataReader as fdr
        except Exception:
            return False

    def get_last_change(self):
        from .models import stock_last_change
        delta, pct = stock_last_change(self)
        return delta, pct

        try:
            df = fdr.DataReader(self.ticker)
            if df is None or df.empty:
                return False
            # 종�? 컬럼 ?�선
            close = df["Close"].iloc[-1]
            prev_price = self.current_price
            self.current_price = close
            self.last_price_updated_at = timezone.now()
            self.save(update_fields=["current_price", "last_price_updated_at", "updated_at"])
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
        verbose_name="?�용??,
    )
    name = models.CharField(max_length=150, verbose_name="채권�?)
    issuer = models.CharField(max_length=150, blank=True, verbose_name="발행�?)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="?�화"
    )
    face_amount = models.DecimalField(
        max_digits=18, decimal_places=2, help_text="?�면총액", verbose_name="?�면총액"
    )
    coupon_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="?�면금리(%)", verbose_name="?�면금리(%)"
    )
    purchase_price_pct = models.DecimalField(
        max_digits=6, decimal_places=3, help_text="매수가(?�면가=100 기�?)", verbose_name="매수가(%)"
    )
    current_price_pct = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True, help_text="?�재가(?�택)", verbose_name="?�재가(%)"
    )
    maturity_date = models.DateField(verbose_name="만기??)
    bond_code = models.CharField(max_length=32, blank=True, help_text="KRX 채권 코드/ISIN (pykrx 조회??", verbose_name="채권코드")
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.currency})"

    def estimated_value(self):
        price_pct = (
            self.current_price_pct if self.current_price_pct is not None else self.purchase_price_pct
        )
        return self.face_amount * (price_pct / 100)

    def update_price_via_pykrx(self):
        """pykrx�?채권 ?�재가(%)�??�데?�트. KRX 코드가 ?�요?????�음.
        구현?� 가???�드?�인?�에 ?�라 ?�순??
        반환: ?�공 ?��?(bool)
        """
        try:
            from pykrx import bond
        except Exception:
            return False

    def get_last_change(self):
        from .models import bond_last_change
        delta_pct, pct = bond_last_change(self)
        return delta_pct, pct

        code = self.bond_code or None
        if not code:
            return False

        try:
            # ?�시: ?�별 ?�세 DataFrame??받아 마�?�?�??�용 (?�드?�인?�는 ?�경??맞게 조정)
            # ?�제 ?�용 가?�한 API??pykrx 버전???�라 ?��? ???�습?�다.
            # 존재?��? ?�으�?False 반환
            today = timezone.localdate().strftime("%Y%m%d")
            try:
                df = bond.get_bond_ohlcv_by_date(today, today, code)
            except Exception:
                df = None

            if df is None or df.empty:
                return False

            # 종�? ?�는 ?��?가격에 ?�당?�는 컬럼 추정
            for col in ["종�?", "Close", "close", "?�익�?, "Price"]:
                if col in df.columns:
                    val = float(df[col].iloc[-1])
                    # % 기�? 가격으�?가??
                    self.current_price_pct = val
                    self.last_price_updated_at = timezone.now()
                    self.save(update_fields=["current_price_pct", "last_price_updated_at", "updated_at"])
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

