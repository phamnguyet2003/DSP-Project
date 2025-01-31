from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, LoginForm, EditProfileForm
from .models import *
from datetime import timedelta
from django.core.cache import cache
from gtts import gTTS
import string
import random
import os
import shutil
# import torch
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts
# import torchaudio

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

def get_index(request): # giao diện để dùng tool
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
    return render(request, 'index.html', {'username':username, 'customer_value': money, 'package':{'name':active_package_name, 'start':active_package_start_date, 'end':active_package_end_date}})

def get_money(request): # nạp tiền
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money
    
    return render(request, 'money.html', {'username':username, 'customer_value': money})

# def get_profile(request): # trang cá nhân
#     if not request.user.is_authenticated:
#         return redirect('login')  # Hoặc trang đăng nhập của bạn
#     username = request.user.name
#     money = request.user.money
#     customer = request.user  # Lấy thông tin từ user đã đăng nhập
#     user = request.user

#     # Kiểm tra nếu người dùng gửi form chỉnh sửa
#     if request.method == "POST":
#         form = EditProfileForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Thông tin đã được cập nhật!')
#             return redirect('profile')  # Redirect lại trang cá nhân sau khi lưu thông tin
#     else:
#         form = EditProfileForm(instance=user)
#     return render(request, 'profile.html', {'username':username, 'customer_value': money, 'customer': customer, 'form':form})


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

# MODEL_PATH = "model/model.pth"
# CONFIG_PATH = "model/config.json"

# config = XttsConfig()
# config.load_json(CONFIG_PATH)
# MODEL = Xtts.init_from_config(config)
# MODEL.load_checkpoint(config, checkpoint_path=MODEL_PATH)

# if torch.cuda.is_available():
#     MODEL.cuda()

# def text_to_speech_xtts(request):
#     text = request.GET.get("text", "Xin chào! Đây là hệ thống TTS của Django.")
#     language = request.GET.get("lang", "vi")  # Ngôn ngữ mặc định là tiếng Việt
    
#     speaker_wav = "sample_speaker.wav"  # Giọng mẫu có sẵn
#     gpt_cond_latent, speaker_embedding = MODEL.get_conditioning_latents(audio_path=speaker_wav)

#     out = MODEL.inference(
#         text=text,
#         language=language,
#         gpt_cond_latent=gpt_cond_latent,
#         speaker_embedding=speaker_embedding,
#         temperature=0.3,
#         length_penalty=1.0,
#         repetition_penalty=10.0,
#         top_k=30,
#         top_p=0.85,
#     )

#     # Tạo đường dẫn file
#     output_filename = f"tts_output.wav"
#     output_path = os.path.join("media", output_filename)

#     # Lưu file âm thanh
#     os.makedirs("media", exist_ok=True)  # Tạo thư mục media nếu chưa có
#     torchaudio.save(output_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)

#     # Trả về file âm thanh để tải xuống
#     with open(output_path, "rb") as f:
#         response = HttpResponse(f.read(), content_type="audio/wav")
#         response["Content-Disposition"] = f"attachment; filename={output_filename}"
    
#     return response

def test_model(request):
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

        dest = shutil.move(full_dir, os.path.join(
            dir, "static/sound/"))

        data = {"loc" :file_name}
        return render(request,'download.html',data)

    return render(request, 'test_model.html')