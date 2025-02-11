from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Customer
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

class CustomPasswordResetForm(forms.Form):
    phone = forms.CharField(max_length=15, label="Số điện thoại")

    def clean_phone(self):
        """ Kiểm tra số điện thoại và lấy email tương ứng """
        phone = self.cleaned_data.get("phone")

        try:
            user = Customer.objects.get(phone=phone)
        except Customer.DoesNotExist:
            raise forms.ValidationError("Số điện thoại chưa được đăng ký.")

        if not user.email:
            raise forms.ValidationError("Tài khoản này không có email khôi phục.")

        self.cleaned_data["email"] = user.email  # Lưu email để sử dụng sau này
        return phone

    def save(self, *args, **kwargs):
        """ Gửi email đặt lại mật khẩu """
        email = self.cleaned_data["email"]
        password_reset_form = PasswordResetForm({'email': email})
        if password_reset_form.is_valid():
            password_reset_form.save(*args, **kwargs)


class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone', 'class': 'form-control'}))

    class Meta:
        model = Customer
        fields = ['username', 'email', 'name', 'phone']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email Address'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Thêm validation cho số điện thoại nếu cần
        if Customer.objects.filter(phone=phone).exists():
            raise forms.ValidationError("A user with that phone already exists.")
        return phone
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Thêm validation cho số điện thoại nếu cần
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    
class EditProfileForm(UserChangeForm):
    name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Customer
        fields = ('name', 'email',)
        