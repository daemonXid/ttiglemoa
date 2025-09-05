from django.urls import path
from .views import registration, auth_views

app_name = 'tm_account'

urlpatterns = [
    # ex: /accounts/signup/
    path('signup/', registration.signup, name='signup'),
    
    # ex: /accounts/login/
    path('login/', auth_views.CustomLoginView.as_view(), name='login'),

    # ex: /accounts/logout/
    path('logout/', auth_views.CustomLogoutView.as_view(), name='logout'),
]
