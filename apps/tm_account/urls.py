from django.urls import path, reverse_lazy
from .views import registration, auth_views, profile_views
from django.contrib.auth import views as auth_views_builtin

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

    # Password Reset URLs
    path('password_reset/', auth_views_builtin.PasswordResetView.as_view(
        template_name='tm_account/password_reset_form.html',
        email_template_name='tm_account/password_reset_email.html',
        success_url=reverse_lazy('tm_account:password_reset_done')
    ), name='password_reset'),

    path('password_reset/done/', auth_views_builtin.PasswordResetDoneView.as_view(
        template_name='tm_account/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views_builtin.PasswordResetConfirmView.as_view(
        template_name='tm_account/password_reset_confirm.html',
        success_url=reverse_lazy('tm_account:password_reset_complete')
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views_builtin.PasswordResetCompleteView.as_view(
        template_name='tm_account/password_reset_complete.html'
    ), name='password_reset_complete'),
]