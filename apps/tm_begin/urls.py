
from django.contrib import admin
from django.urls import path
from . import views


app_name = 'tm_begin'

urlpatterns = [
    path('', views.index, name='index'),
    path("news/", views.investing_news, name="stock_news"),
    path('about/', views.about, name='about'),

]

