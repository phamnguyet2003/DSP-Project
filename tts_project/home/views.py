from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, LoginForm, EditProfileForm
from .models import *
from datetime import timedelta
from django.core.cache import cache
from django.contrib.auth import logout

# model
from gtts import gTTS
import string
import random
import os
import shutil
# Create your views here.
def get_home(request):
    
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money

    return render(request, 'home.html', {'username':username, 'customer_value': money})

def get_payments(request): # mua gói cước
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money
    
    return render(request, 'payments.html', {'username':username, 'customer_value': money})

def get_index(request): # trang dùng tool
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    customer = Customer.objects.get(username=request.user.username)
    
    # Lấy gói dịch vụ active của người dùng
    active_subscription = Subscription.objects.filter(customer=customer, status=True).first()
    if active_subscription:
        active_package_name = active_subscription.package.name 
        active_package_start_date = active_subscription.start_date 
        active_package_end_date = active_subscription.end_date

    username = request.user.name
    money = request.user.money
    
    loc = None  # Khởi tạo biến `loc` cho việc truyền kết quả file âm thanh

    if request.method == "POST":
        letters = string.ascii_lowercase

        file_name = f"{''.join(random.choice(letters) for i in range(10))}.mp3"

        text = request.POST['text']
        tdl = request.POST['tdl']
        lang = request.POST['lang']

        tts = gTTS(text, lang=lang, tld=tdl)
        tts.save(file_name)

        dir = os.getcwd()
        full_dir = os.path.join(dir, file_name)
        print(dir)
        print(full_dir)

        # Di chuyển file vào thư mục tĩnh
        dest = shutil.move(full_dir, os.path.join(dir, "static/sound/"))
        
        # Lưu tên file vào biến loc để hiển thị trên trang
        loc = file_name

    return render(request, 'index.html', {'username': username, 'customer_value': money, 'package': {'name': active_package_name, 'start': active_package_start_date, 'end': active_package_end_date}, 'loc': loc})

def get_money(request): # nạp tiền
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money
    
    return render(request, 'money.html', {'username':username, 'customer_value': money})

def get_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect đến trang đăng nhập nếu chưa đăng nhập
    username = request.user.name
    money = request.user.money
    return render(request, 'profile.html', {'username':username, 'customer_value': money, 'user': request.user})

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        current_password = request.POST.get('current_password')  # Lấy mật khẩu cũ từ form

        # Kiểm tra mật khẩu cũ
        if not request.user.check_password(current_password):
            messages.error(request, 'Mật khẩu cũ không chính xác!')
        else:
            if form.is_valid():
                form.save()  # Cập nhật thông tin nếu mật khẩu đúng
                messages.success(request, 'Cập nhật thông tin thành công!')
                return redirect('profile')  # Redirect lại trang cá nhân

    else:
        form = EditProfileForm(instance=request.user)
    username = request.user.name
    money = request.user.money
    return render(request, 'edit_profile.html', {'username':username, 'customer_value': money,'form': form})

def get_instruction(request): # HDSD
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money
    return render(request, 'instruction.html', {'username':username, 'customer_value': money})

def get_history_use(request): # lịch sử dùng
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money
    return render(request, 'history_use.html', {'username':username, 'customer_value': money})

def get_history_buy(request): # lịch sử mua
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money
    # Lấy thông tin lịch sử nạp tiền từ bảng Wallet
    wallet_history = Wallet.objects.filter(customer=request.user).order_by('-transaction_date')  # Giả sử có trường `date`

    # Lấy thông tin lịch sử mua gói từ bảng Payment
    payment_history = Payment.objects.filter(customer=request.user).order_by('-transaction_date')  # Giả sử có trường `date`

    return render(request, 'history_buy.html', {'username':username, 'customer_value': money, 'wallet_history': wallet_history, 'payment_history': payment_history})

def buy_package(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    name_user = request.user.name
    money = request.user.money

    if request.method == "POST":
        package_id = request.POST.get('package')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        codevoucher = request.POST.get('codevoucher', None)

        try:
            package = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            messages.error(request, 'Gói dịch vụ không tồn tại.')
            return redirect('buy_package')

        # Lấy customer theo username
        try:
            customer = Customer.objects.get(username=request.user.username)
        except Customer.DoesNotExist:
            messages.error(request, 'Khách hàng không tồn tại.')
            return redirect('buy_package')

        # Kiểm tra số dư của khách hàng
        if customer.money < package.price:
            messages.error(request, 'Số dư trong tài khoản không đủ.')
            return redirect('buy_package')

        # # Kiểm tra hành động người dùng đã chọn (Xác nhận mua hoặc Hủy)
        Subscription.objects.filter(customer=customer, status=True).update(status=False)

        # Lưu vào bảng Subscription và Payment
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(days=package.duration)

        Subscription.objects.create(
            customer=customer,
            package=package,
            start_date=start_date,
            end_date=end_date,
            status= True # Cập nhật trạng thái rõ ràng hơn
        )

        Payment.objects.create(
            customer=customer,
            package=package,
            transaction_date=start_date,
            value=package.price
        )

        # Cập nhật số dư của customer
        customer.money -= package.price
        try:
            customer.save()
            print('confirm_button')
            messages.success(request, f"Chúc mừng {customer.name}, bạn đã mua gói {package.name} thành công!")
            return redirect('index')

        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra khi cập nhật số dư: {str(e)}")
            return redirect('home')


    # Lấy tất cả các gói dịch vụ
    packages = Package.objects.all()
    return render(request, 'tem_payment/payment_base.html', {'username': name_user, 'packages': packages, 'customer_value': money})

# Hàm đăng ký người dùng
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Lưu người dùng mới vào cơ sở dữ liệu
            user = form.save()

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

            return redirect('index')  # Điều hướng đến trang chủ sau khi đăng ký thành công
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


def logout_view(request):
    logout(request)  # Đăng xuất người dùng
    return redirect('login')  # Chuyển hướng về trang chủ sau khi đăng xuất

