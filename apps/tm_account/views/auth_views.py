from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36
from django.utils.encoding import force_bytes
from allauth.account.forms import ResetPasswordForm
from django.http import HttpResponseRedirect

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

def custom_password_reset(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                
                # Generate token and uid
                uid = int_to_base36(user.pk)
                key = default_token_generator.make_token(user)

                url = f"/accounts/password/reset/key/{uid}-{key}/"
                return HttpResponseRedirect(url)

            except User.DoesNotExist:
                # Silently fail if user does not exist
                return redirect(reverse_lazy('account_password_reset_done'))
    else:
        form = ResetPasswordForm()
    
    return render(request, 'account/password_reset.html', {'form': form})
