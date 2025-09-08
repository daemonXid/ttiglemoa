from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from ..forms.profile_forms import CustomUserCreationForm

def signup(request):
    if request.method == 'POST':
        # When the form is submitted
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() # Create and save the new user
            # Redirect to the login page after successful registration
            return redirect(reverse_lazy('tm_account:login'))
    else:
        # When the user first visits the page
        form = CustomUserCreationForm()
    
    return render(request, 'tm_account/signup.html', {'form': form})
