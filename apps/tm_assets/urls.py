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
    path("deposits/<int:pk>/edit/", views.edit_deposit, name="edit_deposit"),
    path("deposits/<int:pk>/delete/", views.delete_deposit, name="delete_deposit"),
    path("stocks/new/", views.create_stock, name="create_stock"),
    path("stocks/<int:pk>/edit/", views.edit_stock, name="edit_stock"),
    path("stocks/<int:pk>/delete/", views.delete_stock, name="delete_stock"),
    path("bonds/new/", views.create_bond, name="create_bond"),
    path("bonds/<int:pk>/edit/", views.edit_bond, name="edit_bond"),
    path("bonds/<int:pk>/delete/", views.delete_bond, name="delete_bond"),
    path("refresh/", views.refresh_prices, name="refresh_prices"),
]
