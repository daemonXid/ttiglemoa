from django.urls import path

from . import views

app_name = "tm_assets"

urlpatterns = [
    # 메인 포트폴리오 및 보조 페이지
    path("", views.portfolio_index, name="portfolio"),
    path("allocation/", views.allocation, name="allocation"),

    # 카테고리별 목록 (요약/집계 용도)
    path("deposits/", views.deposits_list, name="deposits_list"),
    path("stocks/", views.stocks_list, name="stocks_list"),
    path("bonds/", views.bonds_list, name="bonds_list"),

    # 생성(Create)
    path("deposits/new/", views.create_deposit, name="create_deposit"),
    path("stocks/new/", views.create_stock, name="create_stock"),
    path("bonds/new/", views.create_bond, name="create_bond"),

    # 수정(Update) / 삭제(Delete) — 본인 소유 항목만 허용
    path("deposits/<int:pk>/edit/", views.edit_deposit, name="edit_deposit"),
    path("deposits/<int:pk>/delete/", views.delete_deposit, name="delete_deposit"),
    path("stocks/<int:pk>/edit/", views.edit_stock, name="edit_stock"),
    path("stocks/<int:pk>/delete/", views.delete_stock, name="delete_stock"),
    path("bonds/<int:pk>/edit/", views.edit_bond, name="edit_bond"),
    path("bonds/<int:pk>/delete/", views.delete_bond, name="delete_bond"),

    # 가격 갱신 후 포트폴리오로 복귀
    path("refresh/", views.refresh_prices, name="refresh_prices"),
]
