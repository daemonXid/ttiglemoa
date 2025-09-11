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
    NONE = "NONE", "단리"
    MONTHLY = "MONTHLY", "월복리"QUARTERLY", "분기복리"
    ANNUALLY = "ANNUALLY", "연복리"KR", "국내"
    US = "US", "해외(미국)"


class DepositSaving(TimeStampedModel):
    class ProductType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "예금"
        SAVING = "SAVING", "적금"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposit_savings",
        verbose_name="사용자"?좏삎"
    )
    bank_name = models.CharField(max_length=100, verbose_name="채권명")
    product_name = models.CharField(max_length=150, verbose_name="채권명"?먭툑"
    )
    annual_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="연이율(%) 예: 3.50",
        verbose_name="?곗씠??%)",
    )
    compounding = models.CharField(
        max_length=16, choices=Compounding.choices, default=Compounding.NONE, verbose_name="蹂듬━ 二쇨린"
    )
    start_date = models.DateField(verbose_name="시작일"留뚭린??)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="통화"
    )

    # ?ъ슜?먭? 吏곸젒 ?낅젰?섎뒗 ?꾩옱 ?됯????좏깮)
    current_value_manual = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="현재가(직접입력)"
    )

    def __str__(self):
        return f"{self.bank_name} {self.product_name} ({self.product_type})"

    def estimated_value(self, as_of=None):
        """
        媛꾨떒 怨꾩궛: ?⑤━ ?먮뒗 ?⑥닚 蹂듬━ 洹쇱궗濡??꾩옱 ?됯???異붿젙.
        current_value_manual ???덉쑝硫??곗꽑 ?ъ슜.
        """
        if self.current_value_manual is not None:
            return self.current_value_manual

        as_of = as_of or timezone.localdate()
        end_date = min(as_of, self.maturity_date) if self.maturity_date else as_of
        days = (end_date - self.start_date).days
        if days <= 0:
            return self.principal_amount

        rate = float(self.annual_rate) / 100.0
        # ?⑤━
        if self.compounding == Compounding.NONE:
            years = days / 365.0
            return self.principal_amount * (1 + rate * years)

        # 蹂듬━ 洹쇱궗
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
        verbose_name="사용자"?쒖옣")
    ticker = models.CharField(max_length=20, verbose_name="티커/종목코드")
    name = models.CharField(max_length=150, blank=True, verbose_name="채권명"?섎웾")
    average_price = models.DecimalField(
        max_digits=18, decimal_places=4, help_text="매수 평균단가 (거래통화)", verbose_name="?됰떒媛"
    )
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="통화"
    )
    current_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True, help_text="현재가 (선택)", verbose_name="?꾩옱媛"
    )
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.ticker} ({self.market})"

    def estimated_value(self):
        price = self.current_price if self.current_price is not None else self.average_price
        return price * self.quantity

    def update_price_via_fdr(self):
        """FinanceDataReader濡?理쒖떊 醫낃? 議고쉶 ??current_price ?낅뜲?댄듃.
        ?쒖옣 援щ텇? 蹂댁“?뺣낫濡??ъ슜?섎ŉ, FDR? KR/US瑜?紐⑤몢 吏??
        諛섑솚: ?깃났 ?щ?(bool)
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
            # 醫낃? 而щ읆 ?곗꽑
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
        verbose_name="사용자"梨꾧텒紐?)
    issuer = models.CharField(max_length=150, blank=True, verbose_name="발행사"통화"
    )
    face_amount = models.DecimalField(
        max_digits=18, decimal_places=2, help_text="액면총액", verbose_name="액면총액"
    )
    coupon_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="액면금리(%)", verbose_name="?쒕㈃湲덈━(%)"
    )
    purchase_price_pct = models.DecimalField(
        max_digits=6, decimal_places=3, help_text="매수가(액면가=100 기준)", verbose_name="留ㅼ닔媛(%)"
    )
    current_price_pct = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True, help_text="현재가(선택)", verbose_name="?꾩옱媛(%)"
    )
    maturity_date = models.DateField(verbose_name="만기일"KRX 梨꾧텒 肄붾뱶/ISIN (pykrx 議고쉶??", verbose_name="만기일")
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.currency})"

    def estimated_value(self):
        price_pct = (
            self.current_price_pct if self.current_price_pct is not None else self.purchase_price_pct
        )
        return self.face_amount * (price_pct / 100)

    def update_price_via_pykrx(self):
        """pykrx濡?梨꾧텒 ?꾩옱媛(%)瑜??낅뜲?댄듃. KRX 肄붾뱶媛 ?꾩슂?????덉쓬.
        援ы쁽? 媛???붾뱶?ъ씤?몄뿉 ?곕씪 ?⑥닚??
        諛섑솚: ?깃났 ?щ?(bool)
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
            # ?덉떆: ?쇰퀎 ?쒖꽭 DataFrame??諛쏆븘 留덉?留?媛??ъ슜 (?붾뱶?ъ씤?몃뒗 ?섍꼍??留욊쾶 議곗젙)
            # ?ㅼ젣 ?ъ슜 媛?ν븳 API??pykrx 踰꾩쟾???곕씪 ?ㅻ? ???덉뒿?덈떎.
            # 議댁옱?섏? ?딆쑝硫?False 諛섑솚
            today = timezone.localdate().strftime("%Y%m%d")
            try:
                df = bond.get_bond_ohlcv_by_date(today, today, code)
            except Exception:
                df = None

            if df is None or df.empty:
                return False

            # 醫낃? ?먮뒗 ?됯?媛寃⑹뿉 ?대떦?섎뒗 而щ읆 異붿젙
            for col in ["醫낃?", "Close", "close", "?섏씡瑜?, "Price"]:
                if col in df.columns:
                    val = float(df[col].iloc[-1])
                    # % 湲곗? 媛寃⑹쑝濡?媛??
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



