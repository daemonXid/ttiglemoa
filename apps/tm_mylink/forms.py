from django import forms
from apps.tm_mylink.models import inquiry_db

class MemoModelForm(forms.ModelForm) :
    class Meta :
        model = inquiry_db
        fields = ['user_title','user_content']