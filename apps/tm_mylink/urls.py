from django.urls import path
from . import views

app_name = 'tm_mylink'

urlpatterns = [
    path('', views.inquiry_write, name='inquiry_write'),
    path('list_all/', views.inquiry_list_all, name='inquiry_list_all'), 
    path('list/', views.inquiry_list, name='inquiry_list'),   
    path('detail/<int:pk>/', views.inquiry_detail, name='inquiry_detail'),
    path('edit/<int:pk>/', views.inquiry_edit, name='inquiry_edit'), 
    path('delete/<int:pk>/', views.inquiry_delete, name='inquiry_delete'), 
]