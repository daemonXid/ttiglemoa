from django.urls import path, reverse_lazy
from .views import registration, auth_views, profile_views

app_name = 'tm_account'

urlpatterns = [
    # ex: /my-account/signup/
    path('signup/', registration.signup, name='signup'),
    
    # ex: /my-account/login/
    path('login/', auth_views.CustomLoginView.as_view(), name='login'),

    # ex: /my-account/logout/
    path('logout/', auth_views.CustomLogoutView.as_view(), name='logout'),

    # ex: /my-account/profile/
    path('profile/', profile_views.profile, name='profile'),

    # ex: /my-account/profile/edit/
    path('profile/edit/', profile_views.profile_edit, name='profile_edit'),

    # ex: /my-account/password_change/
    path('password_change/', profile_views.password_change, name='password_change'),

    # ex: /my-account/delete/
    path('delete/', profile_views.account_delete, name='account_delete'),

    # Custom Password Reset URL
    path('custom_password_reset/', auth_views.custom_password_reset, name='custom_password_reset'),
]
