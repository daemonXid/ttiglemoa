
from django.contrib import admin
from django.urls import path
from . import views


app_name = 'tm_begin'

urlpatterns = [
    path('', views.index, name='index'),
    path('index/json/', views.index_json, name='index_json'),
    path("news/", views.investing_news, name="stock_news"),
    path("news/json/", views.investing_news_json, name="stock_news_json"),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
]

