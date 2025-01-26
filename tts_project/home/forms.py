from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone', 'class': 'form-control'}))

    class Meta:
        model = Customer
        fields = ['username', 'email', 'name', 'phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Thêm validation cho số điện thoại nếu cần
        return phone

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)