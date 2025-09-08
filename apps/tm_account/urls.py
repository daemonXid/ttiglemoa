from django.urls import path
from .views import registration, auth_views, profile_views

app_name = 'tm_account'

urlpatterns = [
    # ex: /accounts/signup/
    path('signup/', registration.signup, name='signup'),
    
    # ex: /accounts/login/
    path('login/', auth_views.CustomLoginView.as_view(), name='login'),

    # ex: /accounts/logout/
    path('logout/', auth_views.CustomLogoutView.as_view(), name='logout'),

    # ex: /accounts/profile/
    path('profile/', profile_views.profile, name='profile'),

    # ex: /accounts/profile/edit/
    path('profile/edit/', profile_views.profile_edit, name='profile_edit'),

    # ex: /accounts/password_change/
    path('password_change/', profile_views.password_change, name='password_change'),

    # ex: /accounts/delete/
    path('delete/', profile_views.account_delete, name='account_delete'),
]
