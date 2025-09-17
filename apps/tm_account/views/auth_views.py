from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages # Import messages
from ..forms.password_forms import DirectPasswordResetForm # Import the new form

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
    By default, it's redirects to LOGOUT_REDIRECT_URL in settings, but we can override it.
    """
    next_page = reverse_lazy('tm_begin:index')

def direct_password_reset(request):
    if request.method == 'POST':
        form = DirectPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password1']
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                messages.success(request, "비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 로그인해주세요.")
                return redirect('tm_account:login')
            except User.DoesNotExist:
                # This case should ideally be caught by form.is_valid() clean_email method
                # but as a fallback
                messages.error(request, "해당 이메일 주소를 가진 사용자를 찾을 수 없습니다.")
        else:
            messages.error(request, "비밀번호 변경에 실패했습니다. 입력값을 확인해주세요.")
    else:
        form = DirectPasswordResetForm()
    
    return render(request, 'tm_account/password_reset.html', {'form': form})
