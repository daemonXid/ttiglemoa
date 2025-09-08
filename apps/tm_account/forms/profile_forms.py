from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# get_user_model() will retrieve the User model specified in AUTH_USER_MODEL
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # Point to the custom User model
        model = User
        # Specify the fields to display in the form
        fields = UserCreationForm.Meta.fields + ('nickname', 'email',)
