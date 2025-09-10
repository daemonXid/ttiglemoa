from django.contrib import admin

from .models import DepositSaving, StockHolding, BondHolding


@admin.register(DepositSaving)
class DepositSavingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product_type",
        "bank_name",
        "product_name",
        "principal_amount",
        "annual_rate",
        "currency",
        "start_date",
        "maturity_date",
    )
    list_filter = ("product_type", "currency", "bank_name")
    search_fields = ("product_name", "bank_name", "user__username")


@admin.register(StockHolding)
class StockHoldingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "market",
        "ticker",
        "name",
        "quantity",
        "average_price",
        "currency",
        "current_price",
        "last_price_updated_at",
    )
    list_filter = ("market", "currency")
    search_fields = ("ticker", "name", "user__username")
    actions = [
        "action_update_stock_prices",
    ]

    def action_update_stock_prices(self, request, queryset):
        updated = 0
        for obj in queryset:
            if obj.update_price_via_fdr():
                updated += 1
        self.message_user(request, f"주식 가격 업데이트: {updated}건 완료")
    action_update_stock_prices.short_description = "선택 주식 FDR 가격 업데이트"


@admin.register(BondHolding)
class BondHoldingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "issuer",
        "currency",
        "face_amount",
        "purchase_price_pct",
        "current_price_pct",
        "bond_code",
        "last_price_updated_at",
        "maturity_date",
    )
    list_filter = ("currency", )
    search_fields = ("name", "issuer", "user__username")
    actions = [
        "action_update_bond_prices",
    ]

    def action_update_bond_prices(self, request, queryset):
        updated = 0
        for obj in queryset:
            if obj.update_price_via_pykrx():
                updated += 1
        self.message_user(request, f"채권 가격 업데이트: {updated}건 완료")
    action_update_bond_prices.short_description = "선택 채권 pykrx 가격 업데이트"
