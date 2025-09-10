from django.urls import path
from .views import inquiry_list,inquiry_write,inquiry_detail,inquiry_edit,inquiry_delete

app_name = 'tm_mylink'

urlpatterns = [
    path('', inquiry_write, name='inquiry_write'),
    path('list/', inquiry_list, name='inquiry_list'),   
    path('detail/<int:pk>/', inquiry_detail, name='inquiry_detail'),
    path('edit/<int:pk>/', inquiry_edit, name='inquiry_edit'), 
    path('delete/<int:pk>/', inquiry_delete, name='inquiry_delete'), 
]