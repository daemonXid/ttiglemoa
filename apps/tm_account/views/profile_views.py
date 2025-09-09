from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from ..forms.profile_forms import ProfileChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout 
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.files import File
from django.conf import settings
import os

@login_required
def profile(request):
    """
    Displays the user's profile page.
    """
    return render(request, 'tm_account/profile.html')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            selected_avatar_path = form.cleaned_data.get('default_avatar')
            if selected_avatar_path:
                full_static_path = os.path.join(settings.BASE_DIR, selected_avatar_path)
                if os.path.exists(full_static_path):
                    with open(full_static_path, 'rb') as f:
                        django_file = File(f)
                        # The second argument to save() is the filename that will be stored in the database
                        user.profile_image.save(os.path.basename(full_static_path), django_file, save=False)
            
            # If the user checks the "clear" checkbox for the profile_image field,
            # form.cleaned_data['profile_image'] will be False.
            # In that case, we should clear the field.
            if form.cleaned_data.get('profile_image') is False:
                user.profile_image = None

            user.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return HttpResponseRedirect(reverse_lazy('tm_account:profile'))
        else:
            messages.error(request, '오류가 발생했습니다. 입력 내용을 확인해주세요.')
    else:
        form = ProfileChangeForm(instance=request.user)
    return render(request, 'tm_account/profile_edit.html', {'form': form})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important! Keeps the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse_lazy('tm_account:profile'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'tm_account/password_change.html', {'form': form})

@login_required
def account_delete(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate the user with the provided password
            user = authenticate(request, username=request.user.username, password=form.cleaned_data['password'])
            if user is not None:
                # Password is correct, delete the user
                user.delete()
                logout(request) # Log out the user after deletion
                messages.success(request, 'Your account has been successfully deleted.')
                return HttpResponseRedirect(reverse_lazy('tm_begin:index')) # Redirect to main page
            else:
                messages.error(request, 'Incorrect password. Please try again.')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AuthenticationForm(request) # For GET request, show an empty form
    return render(request, 'tm_account/account_delete_confirm.html', {'form': form})