from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()

class DirectPasswordResetForm(forms.Form):
    email = forms.EmailField(label="이메일 주소", max_length=254)
    new_password1 = forms.CharField(
        label="새 비밀번호",
        widget=forms.PasswordInput,
        strip=False,
        help_text="8자 이상이어야 하며, 일반적인 단어가 아니어야 합니다. 또한, 숫자를 포함할 수 없습니다."
    )
    new_password2 = forms.CharField(
        label="새 비밀번호 확인",
        widget=forms.PasswordInput,
        strip=False,
        help_text="비밀번호를 다시 입력해주세요."
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("해당 이메일 주소를 가진 사용자를 찾을 수 없습니다.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', "비밀번호가 일치하지 않습니다.")
        
        # Basic password validation (can be extended with custom validators)
        if new_password1 and len(new_password1) < 8:
            self.add_error('new_password1', "비밀번호는 8자 이상이어야 합니다.")
        
        # Example: Check for common words or numbers (as per help_text)
        # This is a very basic check, real-world validation would be more robust.
        if new_password1 and (new_password1.lower() in ['password', '12345678'] or any(char.isdigit() for char in new_password1)):
             self.add_error('new_password1', "비밀번호는 일반적인 단어이거나 숫자를 포함할 수 없습니다.")

        return cleaned_data

    def save(self, user):
        user.set_password(self.cleaned_data['new_password1'])
        user.save()

