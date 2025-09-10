from django.urls import path

from . import views

app_name = "tm_assets"

urlpatterns = [
    path("", views.portfolio_index, name="portfolio"),
    path("allocation/", views.allocation, name="allocation"),
    path("deposits/", views.deposits_list, name="deposits_list"),
    path("stocks/", views.stocks_list, name="stocks_list"),
    path("bonds/", views.bonds_list, name="bonds_list"),
    path("deposits/new/", views.create_deposit, name="create_deposit"),
    path("stocks/new/", views.create_stock, name="create_stock"),
    path("bonds/new/", views.create_bond, name="create_bond"),
    path("refresh/", views.refresh_prices, name="refresh_prices"),
]
