from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from ..forms.profile_forms import ProfileChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout 
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm 

@login_required
def profile(request):
    """
    Displays the user's profile page.
    """
    return render(request, 'tm_account/profile.html')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('tm_account:profile'))
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
            return redirect(reverse_lazy('tm_account:profile'))
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
                return redirect(reverse_lazy('tm_begin:index')) # Redirect to main page
            else:
                messages.error(request, 'Incorrect password. Please try again.')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AuthenticationForm(request) # For GET request, show an empty form
    return render(request, 'tm_account/account_delete_confirm.html', {'form': form})