
from django.contrib import admin
from django.urls import path
from . import views
from . import test_4views


app_name = 'tm_begin'

urlpatterns = [
    path('', views.index, name='index'),
    path("news/", views.investing_news, name="stock_news"),
    # path("news/", okay_views.stock_news, name="stock_news"),

]
