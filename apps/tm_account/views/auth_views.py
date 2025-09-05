from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    """
    This view uses Django's built-in LoginView.
    We just need to tell it which template to use.
    """
    template_name = 'tm_account/login.html'
    # After a successful login, Django will look for this URL.
    # We haven't created it yet, but it will be the user's main dashboard or profile page.
    success_url = reverse_lazy('tm_begin:index') 

class CustomLogoutView(LogoutView):
    """
    The built-in LogoutView doesn't require much configuration.
    It logs the user out and redirects.
    By default, it redirects to LOGOUT_REDIRECT_URL in settings, but we can override it.
    """
    next_page = reverse_lazy('tm_begin:index')
