from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, LoginForm, EditProfileForm , CustomPasswordResetForm
from .models import *
from datetime import timedelta
from django.core.cache import cache
from django.contrib.auth import logout
from django.db.models import Q
import os
import shutil
import random
import string
from django.conf import settings
from django.urls import reverse
import zipfile

# model
from gtts import gTTS

# forgot password
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView

############
# Chỉ thay đổi 1 phần html, không load lại cả trang
from django.http import JsonResponse


def get_index(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    customer = Customer.objects.get(username=request.user.username)
    active_subscription = Subscription.objects.filter(customer=customer, status=True).first()

    char_limit = 500  # Mặc định cho gói Free
    active_package_name = None
    active_package_start_date = None
    active_package_end_date = None

    if active_subscription:
        active_package_name = active_subscription.package.name 
        active_package_start_date = active_subscription.start_date 
        active_package_end_date = active_subscription.end_date

        if active_package_name == 'Normal Package':
            char_limit = 5000
        elif active_package_name == 'Pro Package':
            char_limit = None  

    username = request.user.name
    money = request.user.money
    
    # Xóa file cũ nếu tồn tại trong session
    loc = request.session.get('loc')
    if loc:
        old_file_path = os.path.join(settings.BASE_DIR, "static/sound", loc)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)  # Xóa file cũ
        del request.session['loc']  # Xóa khỏi session
        
    return render(request, 'index.html', {
        'username': username, 
        'customer_value': money, 
        'package': {'name': active_package_name, 'start': active_package_start_date, 'end': active_package_end_date}, 
        'char_limit': char_limit, 
        'loc': loc
    })
    # return render(request, "test.html")

def submit_input(request):
    customer = Customer.objects.get(username=request.user.username)
    active_subscription = Subscription.objects.filter(customer=customer, status=True).first()

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        letters = string.ascii_lowercase
        file_name = f"{''.join(random.choice(letters) for i in range(10))}.mp3"

        text = request.POST['text']
        tdl = request.POST['tdl']
        lang = request.POST['lang']

        tts = gTTS(text, lang=lang, tld=tdl)
        tts.save(file_name)

        # Đường dẫn thư mục
        base_dir = os.getcwd()
        sound_dir = os.path.join(base_dir, "static/sound/")
        input_dir = os.path.join(base_dir, "static/history/input_text/")
        output_dir = os.path.join(base_dir, "static/history/output_audio/")

        # Đảm bảo thư mục tồn tại
        os.makedirs(sound_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Di chuyển file MP3 vào static/sound/
        mp3_path = shutil.move(file_name, sound_dir)

        # Tạo file ZIP
        zip_name = f"{os.path.splitext(file_name)[0]}.zip"
        zip_path = os.path.join(output_dir, zip_name)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(mp3_path, os.path.basename(mp3_path))
            
        # Lưu file ZIP chứa input_text.txt
        text_zip_path = os.path.join(input_dir, zip_name)
        with zipfile.ZipFile(text_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("input_text.txt", text)

        # Lưu tên file vào session
        request.session['loc'] = file_name
        loc = file_name
        
        # Lưu vào History
        History.objects.create(
            customer=customer,
            timestamp=now(),
            input_text=" ".join(text.split()[:10]) + "...",  # 10 từ đầu tiên
            text_file=zip_name, # static\history\input_text
            voice_file=zip_name, # static\history\output_audio
            package=active_subscription.package
        )
        return JsonResponse({"success": True, "loc": file_name}) # Trả về danh sách dữ liệu đã nộp

############




# Create your views here.
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset.html'  # Đảm bảo đây là template đúng
    def form_valid(self, form):
        email = form.cleaned_data.get("email", "")
        
        # Che một phần email để bảo mật
        at_index = email.find('@')
        if at_index > 3:
            masked_email = '*' * (at_index - 3) + email[at_index - 3:]
        else:
            masked_email = email  # Nếu email quá ngắn thì giữ nguyên

        # Lưu vào session để sử dụng ở trang `password_reset_done.html`
        self.request.session['masked_email'] = masked_email

        return super().form_valid(form)
    
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['masked_email'] = self.request.session.get('masked_email', '')
        return context
    
def get_home(request):
    
    if not request.user.is_authenticated:
        customers_count = Customer.objects.count()
        return render(request, 'home_not_log_in.html', { "customers_count": customers_count})  # Hoặc trang đăng nhập của bạn
    
    customers_count = Customer.objects.count()
    username = request.user.name
    money = request.user.money

    return render(request, 'home.html', {'username':username, 'customer_value': money, "customers_count": customers_count})

def get_payments(request): # mua gói cước
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money
    
    return render(request, 'payments.html', {'username':username, 'customer_value': money})

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
    use_history = History.objects.filter(customer=request.user).order_by('-timestamp')  # Giả sử có trường `date`
    
    return render(request, 'history_use.html', {'username':username, 'customer_value': money, 'use_history': use_history})

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
            # messages.error(request, 'Gói dịch vụ không tồn tại.')
            return redirect('buy_package')

        # Lấy customer theo username
        try:
            customer = Customer.objects.get(username=request.user.username)
        except Customer.DoesNotExist:
            # messages.error(request, 'Khách hàng không tồn tại.')
            return redirect('buy_package')

        # Kiểm tra số dư của khách hàng
        if customer.money < package.price:
            # messages.error(request, 'Số dư trong tài khoản không đủ.')
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
            # messages.success(request, f"Chúc mừng {customer.name}, bạn đã mua gói {package.name} thành công!")
            return redirect('index')

        except Exception as e:
            # messages.error(request, f"Có lỗi xảy ra khi cập nhật số dư: {str(e)}")
            return redirect('home')


    # Lấy tất cả các gói dịch vụ
    # packages = Package.objects.all()
    packages = Package.objects.filter(Q(name="Normal Package") | Q(name="Pro Package"))

    return render(request, 'tem_payment/payment_base.html', {'username': name_user, 'packages': packages, 'customer_value': money})

# Hàm đăng ký người dùng
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Lưu người dùng mới vào cơ sở dữ liệu
            user = form.save()

            # Kiểm tra xem người dùng đã có Subscription chưa
            if not Subscription.objects.filter(customer=user).exists():
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
    return redirect('home')  # Chuyển hướng về trang chủ sau khi đăng xuất

