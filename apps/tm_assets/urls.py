from django.urls import path

from . import views

app_name = "tm_assets"

urlpatterns = [
    # 메인 포트폴리오 및 분석 페이지
    path("", views.portfolio_index, name="portfolio"),
    path("allocation/", views.allocation, name="allocation"),

    # 자산별 목록 페이지
    path("deposits/", views.deposits_list, name="deposits_list"),
    path("stocks/", views.stocks_list, name="stocks_list"),
    path("bonds/", views.bonds_list, name="bonds_list"),

    # 예적금 CRUD
    path("deposits/create/", views.create_deposit, name="create_deposit"),
    path("deposits/<int:pk>/", views.edit_deposit, name="edit_deposit"),
    path("deposits/<int:pk>/delete/", views.delete_deposit, name="delete_deposit"),

    # 주식 CRUD
    path("stocks/create/", views.create_stock, name="create_stock"),
    path("stocks/<int:pk>/", views.edit_stock, name="edit_stock"),
    path("stocks/<int:pk>/delete/", views.delete_stock, name="delete_stock"),

    # 채권 CRUD
    path("bonds/create/", views.create_bond, name="create_bond"),
    path("bonds/<int:pk>/", views.edit_bond, name="edit_bond"),
    path("bonds/<int:pk>/delete/", views.delete_bond, name="delete_bond"),

    # 기타 기능
    path("refresh-prices/", views.refresh_prices, name="refresh_prices"),
]
