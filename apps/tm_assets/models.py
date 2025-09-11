from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Currency(models.TextChoices):
    KRW = "KRW", "¿øÈ­(KRW)"
    USD = "USD", "´Ş·¯(USD)"
    JPY = "JPY", "¿£(JPY)"
    EUR = "EUR", "À¯·Î(EUR)"


class Compounding(models.TextChoices):
    NONE = "NONE", "´Ü¸®"
    MONTHLY = "MONTHLY", "?”ë³µë¦?
    QUARTERLY = "QUARTERLY", "ë¶„ê¸°ë³µë¦¬"
    ANNUALLY = "ANNUALLY", "?°ë³µë¦?


class Market(models.TextChoices):
    KR = "KR", "±¹³»"
    US = "US", "ÇØ¿Ü(¹Ì±¹)"


class DepositSaving(TimeStampedModel):
    class ProductType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "¿¹±İ"
        SAVING = "SAVING", "Àû±İ"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposit_savings",
        verbose_name="?¬ìš©??,
    )
    product_type = models.CharField(
        max_length=16, choices=ProductType.choices, verbose_name="? í˜•"
    )
    bank_name = models.CharField(max_length=100, verbose_name="?€?‰ëª…")
    product_name = models.CharField(max_length=150, verbose_name="?í’ˆëª?)
    principal_amount = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name="?ê¸ˆ"
    )
    annual_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="?°ì´??%) ?? 3.50",
        verbose_name="?°ì´??%)",
    )
    compounding = models.CharField(
        max_length=16, choices=Compounding.choices, default=Compounding.NONE, verbose_name="ë³µë¦¬ ì£¼ê¸°"
    )
    start_date = models.DateField(verbose_name="?œì‘??)
    maturity_date = models.DateField(null=True, blank=True, verbose_name="ë§Œê¸°??)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="?µí™”"
    )

    # ?¬ìš©?ê? ì§ì ‘ ?…ë ¥?˜ëŠ” ?„ì¬ ?‰ê???? íƒ)
    current_value_manual = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="?‰ê???ì§ì ‘?…ë ¥)"
    )

    def __str__(self):
        return f"{self.bank_name} {self.product_name} ({self.product_type})"

    def estimated_value(self, as_of=None):
        """
        ê°„ë‹¨ ê³„ì‚°: ?¨ë¦¬ ?ëŠ” ?¨ìˆœ ë³µë¦¬ ê·¼ì‚¬ë¡??„ì¬ ?‰ê???ì¶”ì •.
        current_value_manual ???ˆìœ¼ë©??°ì„  ?¬ìš©.
        """
        if self.current_value_manual is not None:
            return self.current_value_manual

        as_of = as_of or timezone.localdate()
        end_date = min(as_of, self.maturity_date) if self.maturity_date else as_of
        days = (end_date - self.start_date).days
        if days <= 0:
            return self.principal_amount

        rate = float(self.annual_rate) / 100.0
        # ?¨ë¦¬
        if self.compounding == Compounding.NONE:
            years = days / 365.0
            return self.principal_amount * (1 + rate * years)

        # ë³µë¦¬ ê·¼ì‚¬
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
        verbose_name="?¬ìš©??,
    )
    market = models.CharField(max_length=8, choices=Market.choices, verbose_name="?œì¥")
    ticker = models.CharField(max_length=20, verbose_name="?°ì»¤/ì¢…ëª©ì½”ë“œ")
    name = models.CharField(max_length=150, blank=True, verbose_name="ì¢…ëª©ëª?)
    quantity = models.DecimalField(max_digits=18, decimal_places=4, verbose_name="?˜ëŸ‰")
    average_price = models.DecimalField(
        max_digits=18, decimal_places=4, help_text="ë§¤ìˆ˜?‰ê· ?¨ê? (ê±°ë˜?µí™”)", verbose_name="?‰ë‹¨ê°€"
    )
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="?µí™”"
    )
    current_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True, help_text="?„ì¬ê°€ (? íƒ)", verbose_name="?„ì¬ê°€"
    )
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.ticker} ({self.market})"

    def estimated_value(self):
        price = self.current_price if self.current_price is not None else self.average_price
        return price * self.quantity

    def update_price_via_fdr(self):
        """FinanceDataReaderë¡?ìµœì‹  ì¢…ê? ì¡°íšŒ ??current_price ?…ë°?´íŠ¸.
        ?œì¥ êµ¬ë¶„?€ ë³´ì¡°?•ë³´ë¡??¬ìš©?˜ë©°, FDR?€ KR/USë¥?ëª¨ë‘ ì§€??
        ë°˜í™˜: ?±ê³µ ?¬ë?(bool)
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
            # ì¢…ê? ì»¬ëŸ¼ ?°ì„ 
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
        verbose_name="?¬ìš©??,
    )
    name = models.CharField(max_length=150, verbose_name="ì±„ê¶Œëª?)
    issuer = models.CharField(max_length=150, blank=True, verbose_name="ë°œí–‰ì²?)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.KRW, verbose_name="?µí™”"
    )
    face_amount = models.DecimalField(
        max_digits=18, decimal_places=2, help_text="?¡ë©´ì´ì•¡", verbose_name="?¡ë©´ì´ì•¡"
    )
    coupon_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="?œë©´ê¸ˆë¦¬(%)", verbose_name="?œë©´ê¸ˆë¦¬(%)"
    )
    purchase_price_pct = models.DecimalField(
        max_digits=6, decimal_places=3, help_text="ë§¤ìˆ˜ê°€(?¡ë©´ê°€=100 ê¸°ì?)", verbose_name="ë§¤ìˆ˜ê°€(%)"
    )
    current_price_pct = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True, help_text="?„ì¬ê°€(? íƒ)", verbose_name="?„ì¬ê°€(%)"
    )
    maturity_date = models.DateField(verbose_name="ë§Œê¸°??)
    bond_code = models.CharField(max_length=32, blank=True, help_text="KRX ì±„ê¶Œ ì½”ë“œ/ISIN (pykrx ì¡°íšŒ??", verbose_name="ì±„ê¶Œì½”ë“œ")
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.currency})"

    def estimated_value(self):
        price_pct = (
            self.current_price_pct if self.current_price_pct is not None else self.purchase_price_pct
        )
        return self.face_amount * (price_pct / 100)

    def update_price_via_pykrx(self):
        """pykrxë¡?ì±„ê¶Œ ?„ì¬ê°€(%)ë¥??…ë°?´íŠ¸. KRX ì½”ë“œê°€ ?„ìš”?????ˆìŒ.
        êµ¬í˜„?€ ê°€???”ë“œ?¬ì¸?¸ì— ?°ë¼ ?¨ìˆœ??
        ë°˜í™˜: ?±ê³µ ?¬ë?(bool)
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
            # ?ˆì‹œ: ?¼ë³„ ?œì„¸ DataFrame??ë°›ì•„ ë§ˆì?ë§?ê°??¬ìš© (?”ë“œ?¬ì¸?¸ëŠ” ?˜ê²½??ë§ê²Œ ì¡°ì •)
            # ?¤ì œ ?¬ìš© ê°€?¥í•œ API??pykrx ë²„ì „???°ë¼ ?¤ë? ???ˆìŠµ?ˆë‹¤.
            # ì¡´ì¬?˜ì? ?Šìœ¼ë©?False ë°˜í™˜
            today = timezone.localdate().strftime("%Y%m%d")
            try:
                df = bond.get_bond_ohlcv_by_date(today, today, code)
            except Exception:
                df = None

            if df is None or df.empty:
                return False

            # ì¢…ê? ?ëŠ” ?‰ê?ê°€ê²©ì— ?´ë‹¹?˜ëŠ” ì»¬ëŸ¼ ì¶”ì •
            for col in ["ì¢…ê?", "Close", "close", "?˜ìµë¥?, "Price"]:
                if col in df.columns:
                    val = float(df[col].iloc[-1])
                    # % ê¸°ì? ê°€ê²©ìœ¼ë¡?ê°€??
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

