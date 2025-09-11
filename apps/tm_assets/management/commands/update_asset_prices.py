from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.tm_assets.models import StockHolding, BondHolding
from apps.tm_assets.models import DepositSaving, DepositValueHistory


class Command(BaseCommand):
    help = "Update stock and bond prices using FinanceDataReader and pykrx"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, default=None, help="username to limit update")
        parser.add_argument("--only", type=str, choices=["stock", "bond"], default=None)

    def handle(self, *args, **options):
        username = options.get("user")
        only = options.get("only")

        user = None
        if username:
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"User '{username}' not found"))
                return

        total_stock = total_bond = 0
        ok_stock = ok_bond = 0

        if only in (None, "stock"):
            qs = StockHolding.objects.all()
            if user:
                qs = qs.filter(user=user)
            total_stock = qs.count()
            for s in qs.iterator():
                if s.update_price_via_fdr():
                    ok_stock += 1

        if only in (None, "bond"):
            qs = BondHolding.objects.all()
            if user:
                qs = qs.filter(user=user)
            total_bond = qs.count()
            for b in qs.iterator():
                if b.update_price_via_pykrx():
                    ok_bond += 1

        # snapshot deposits
        if only is None:
            dqs = DepositSaving.objects.all()
            if user:
                dqs = dqs.filter(user=user)
            for d in dqs.iterator():
                try:
                    DepositValueHistory.objects.create(deposit=d, value=d.estimated_value())
                except Exception:
                    pass

        self.stdout.write(
            self.style.SUCCESS(
                f"Stocks: {ok_stock}/{total_stock} updated, Bonds: {ok_bond}/{total_bond} updated"
            )
        )
