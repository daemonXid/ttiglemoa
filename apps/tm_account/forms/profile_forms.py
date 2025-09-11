from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

# Choices for default avatars
DEFAULT_AVATAR_CHOICES = [
    ('tm_account/images/avatars/avatar1.svg', '빨강'),
    ('tm_account/images/avatars/avatar2.svg', '파랑'),
    ('tm_account/images/avatars/avatar3.svg', '초록'),
]

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('nickname', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nickname'].label = "닉네임"
        self.fields['email'].label = "이메일"

class ProfileChangeForm(forms.ModelForm):
    # Field for selecting a default avatar
    default_avatar = forms.ChoiceField(
        choices=[('', '--------- (기본 아바타 선택)')] + DEFAULT_AVATAR_CHOICES,
        required=False,
        widget=forms.RadioSelect,
        label="기본 아바타 선택"
    )

    class Meta:
        model = User
        fields = ('nickname', 'email', 'profile_image')
        widgets = {
            'profile_image': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nickname'].label = "닉네임"
        self.fields['email'].label = "이메일"
        self.fields['profile_image'].label = "새 프로필 사진 업로드"
        self.fields['profile_image'].required = False
