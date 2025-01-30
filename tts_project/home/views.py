from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import RegisterForm
from .forms import RegisterForm, LoginForm
from .models import *
from datetime import timedelta


# Create your views here.
def get_home(request):
    username = request.user.name
    return render(request, 'home.html', {'username':username})

def get_payments(request): # mua gói cước
    username = request.user.name
    return render(request, 'payments.html', {'username':username})

def get_index(request): # giao diện để dùng tool
    username = request.user.name
    return render(request, 'index.html', {'username':username})

def get_money(request): # nạp tiền
    username = request.user.name
    return render(request, 'money.html', {'username':username})

def get_profile(request): # trang cá nhân
    username = request.user.name
    return render(request, 'profile.html', {'username':username})

def get_instruction(request): # HDSD
    username = request.user.name
    return render(request, 'instruction.html', {'username':username})

def get_history_use(request): # lịch sử dùng
    username = request.user.name
    return render(request, 'history_use.html', {'username':username})

def get_history_buy(request): # lịch sử mua
    username = request.user.name
    return render(request, 'history_buy.html', {'username':username})

# Hàm đăng ký người dùng
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Lưu người dùng mới vào cơ sở dữ liệu
            user = form.save()


            # Tạo Wallet cho Customer mới
            wallet = Wallet.objects.create(customer=user, value=0, old_value=0)

            # Tạo Subscription với ID_Pack=1 (Active = 1)
            try:
                package = Package.objects.get(id=1)  # ID 1 là gói mặc định
                start_date = timezone.now().date()
                end_date = start_date + timedelta(package.duration)  # Ví dụ: thuê bao trong 30 ngày
                subscription = Subscription.objects.create(
                    customer=user,
                    package=package,
                    start_date=start_date,
                    end_date=end_date,
                    status=True  # Active = 1
                )
            except Package.DoesNotExist:
                print("Package with ID=1 does not exist.")
                
                
            # Đăng nhập người dùng sau khi đăng ký
            auth_login(request, user)

            return redirect('home')  # Điều hướng đến trang chủ sau khi đăng ký thành công
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

# Hàm đăng nhập người dùng
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Xác thực người dùng
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)  # Đăng nhập người dùng
                return redirect('home')  # Điều hướng đến trang chủ sau khi đăng nhập
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

