import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, LoginForm, EditProfileForm , CustomPasswordResetForm
from .models import *
from datetime import timedelta
# from django.core.cache import cache
from django.contrib.auth import logout
from django.db.models import Q, Sum
import os
import re
import datetime
from django.conf import settings
from django.http import HttpResponse , JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

# forgot password
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.utils.timezone import now
import io

from .gradio_client_file import client
from gradio_client import handle_file
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile

# Ghi log
import logging
logger = logging.getLogger('django')
def my_view(request):
    logger.info(f"User {request.user.username} accessed my_view")
    return HttpResponse("Hello, logging!")

from django.shortcuts import render
from django.http import HttpResponse, FileResponse

###########################
# Voice Clone
def upload_audio(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    
    active_subscription = Subscription.objects.filter(customer=request.user, status=True).first()
    
    if not active_subscription or active_subscription.package.name != "Pro Package":
        return redirect('buy_package')  # Hoặc trang đăng nhập của bạn
        
    money = request.user.money
    username = request.user.name
    
    
    if request.method == 'POST':
        customer = Customer.objects.get(username=request.user.username)
        name = customer.username
        audioname = request.POST.get('audioname')
        uploaded_file = request.FILES.get('file')

        # Kiểm tra nếu tên file đã tồn tại
        if AudioSample.objects.filter(customer=customer, audioname=audioname).exists():
            return JsonResponse({"status": "error", "error": "Tên file này đã tồn tại. Vui lòng chọn tên khác."}, status=400)

        try:
            audio_data = uploaded_file.read()

            # Lưu vào AudioSample
            audio_sample = AudioSample(
                customer=customer,
                audioname=audioname,
                audio_data=audio_data
            )
            audio_sample.save()
            return redirect('display_audio')
        except Exception as e:
            return JsonResponse({"status": "error", "error": f"Lỗi khi lưu file: {str(e)}"}, status=500)

    return render(request, 'upload_audio.html', {'username':username, 'customer_value': money})

def get_audio(request):
    audioname = request.GET.get('audioname')
    if not audioname:
        return HttpResponse("Missing 'audioname' parameter", status=400)

    try:
        audio_sample = AudioSample.objects.get(audioname=audioname)
        audio_buffer = io.BytesIO(audio_sample.audio_data)  # Chuyển `memoryview` thành file-like object

        # Trả file về trình duyệt để phát
        response = FileResponse(audio_buffer, content_type='audio/mpeg')
        response['Content-Disposition'] = f'inline; filename="{audioname}.mp3"'  # Không tải về mà phát trực tiếp
        return response

    except AudioSample.DoesNotExist:
        return HttpResponse("Audio file not found", status=404)
def display_audio(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    
    active_subscription = Subscription.objects.filter(customer=request.user, status=True).first()
    if not active_subscription or active_subscription.package.name != "Pro Package":
        return redirect('buy_package')  # Hoặc trang đăng nhập của bạn
        
    money = request.user.money
    customer = request.user  # Lấy user hiện tại
    audio_samples = AudioSample.objects.filter(customer=customer)  # Lấy tất cả audio của user
    
    return render(request, 'display_audio.html', {'audio_samples': audio_samples, 'username':customer.name, 'customer_value': money})

def send_audio_to_gradio(request):
    customer = Customer.objects.get(username=request.user.username)
    audioname = request.GET.get('audioname')
    if not audioname:
        return JsonResponse({"error": "Missing 'audioname' parameter"}, status=400)

    try:
        # Lấy dữ liệu từ database
        audio_sample = AudioSample.objects.get(audioname=audioname, customer=request.user)

        # Tạo file tạm thời để lưu dữ liệu
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(audio_sample.audio_data)
            temp_audio.flush()  # Đảm bảo dữ liệu được ghi hoàn chỉnh
            temp_audio_path = temp_audio.name  # Lấy đường dẫn file

        # Gọi hàm handle_file() để lấy đường dẫn chính xác
        processed_file_path = handle_file(temp_audio_path)

        # Gửi file lên Gradio API
        result = client.predict(
            audio_path=processed_file_path,  # Đúng định dạng của handle_file()
            name=f'{customer.username}_{audioname}',
            api_name="/process_voice_clone"
        )
        # Xóa file tạm sau khi sử dụng xong (nếu cần)
        audio_sample.gradioname = result[len('Voice successfully cloned and saved as: '):]
        audio_sample.save()
        os.remove(temp_audio_path)
        return redirect('display_audio')

    except AudioSample.DoesNotExist:
        return JsonResponse({"error": "Audio file not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
###########################
#  Trang trải nghiệm
def get_index(request):
    if not request.user.is_authenticated:
        return redirect('login')

    customer = Customer.objects.get(username=request.user.username)
    audioSample = AudioSample.objects.filter(customer=request.user)
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

    username = customer.name
    money = customer.money
    
    # Xóa file cũ nếu tồn tại trong session
    loc = request.session.get('loc', None)
    if loc:
        old_file_path = os.path.join(settings.MEDIA_ROOT, "sound", loc)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)  # Xóa file cũ
        request.session.pop('loc', None)  # Xóa loc trong session
        request.session.modified = True  # Cập nhật session
    # media_url = settings.MEDIA_URL
    # print(media_url)
    return render(request, 'index.html', {
        'username': username, 
        'customer_value': money, 
        'package': {'name': active_package_name, 'start': active_package_start_date, 'end': active_package_end_date}, 
        'char_limit': char_limit, 
        'loc': loc,
        'audioSample': audioSample
    })

def get_private_audio(request):
    customer = Customer.objects.get(username=request.user.username)
    active_subscription = Subscription.objects.filter(customer=customer, status=True).first()

    if request.method == "GET":
        # Lấy thông tin request
        username = request.user.username
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{username}_{timestamp}.mp3"

        text = request.GET.get('text', '')
        tdl = request.GET.get('tdl', 'None')
        lang = request.GET.get('lang', 'vi')
        spl = request.GET.get('spl', '/content/model/samples/nu-luu-loat.wav')
        isDownload = request.GET.get('isDownload', "false")

        result = client.predict(
		prompt=text,
		language=lang,
		audio_file_pth=spl, # tạo list
		normalize_text=True,
		target_language=tdl if tdl != "None" else None,   # đoạn này trong html thì tạo check list các support language cho user
  		username= customer.username,
		api_name="/predict",
  
        )
        audio_path = result[0]  # API trả về đường dẫn file âm thanh từ Gradio
        time_match = re.search(r"Time to generate audio: (\d+) milliseconds", result[1])
        rtf_match = re.search(r"Real-time factor \(RTF\): ([\d.]+)", result[1])

        if time_match and rtf_match:
            duration = round(int(time_match.group(1)) / 1000/float(rtf_match.group(1)),2)
        # Đọc file âm thanh từ Gradio
        try:
            with open(audio_path, "rb") as f:
                audio_data = f.read()
        except Exception as e:
            return HttpResponse(f"Lỗi khi đọc file âm thanh: {str(e)}", status=500)


        # Lưu lịch sử nếu không phải chế độ tải xuống
        if isDownload == "false":
            History.objects.create(
                customer=request.user,
                timestamp=now(),
                text_preview=" ".join(text.split()[:10]) + ("..." if len(text.split()) > 10 else ""),
                character_count=len(text),
                duration=duration,
                package=active_subscription.package if active_subscription else None,
                cost=None
            )

        # Lưu lại đường dẫn của file mới trong session
        request.session['loc'] = file_name  
        request.session.modified = True  

        # Trả file âm thanh về frontend
        response = HttpResponse(audio_data, content_type="audio/mpeg")
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response
    
#####################################
# Bảng donation
def donation_list(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Hoặc trang đăng nhập của bạn
    username = request.user.name
    money = request.user.money
    
    """Hiển thị danh sách donation"""
    # donations = Donation.objects.order_by('-created_at')  # Sắp xếp mới nhất lên đầu
    donations = Donation.objects.values('customer__name').annotate(total_amount=Sum('amount')).order_by('-total_amount')
    user_donations = Donation.objects.filter(customer=request.user).order_by('-created_at')  # Lịch sử của user
    return render(request, 'donation_list.html', {'donations': donations, 'user_donations': user_donations, 'username':username, 'customer_value': money})

def donate(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        message = request.POST.get('message', '')
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0")

            # Lưu donation, trừ tiền sẽ được xử lý trong model
            donation = Donation.objects.create(customer=request.user, amount=amount, message=message)
            messages.success(request, f"Cảm ơn bạn đã donate {amount} VNĐ! Lời nhắn: {message}")

        except ValueError as e:
            messages.error(request, f"Lỗi: {e}")
        except Exception as e:
            messages.error(request, "Có lỗi xảy ra!")

        return redirect('donation_list')

#####################################
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
 
def track_page_view():
    today = now().date()
    page_view, created = PageView.objects.get_or_create(date=today)
    page_view.count += 1
    page_view.save()
       
def get_home(request):
    
    if not request.user.is_authenticated:
        today = now().date()
        page_view = PageView.objects.filter(date=today).first()
        visit_count = page_view.count if page_view else 0
        customers_count = Customer.objects.count()
        return render(request, 'home_not_log_in.html', { "customers_count": customers_count, "visit_count":visit_count})  # Hoặc trang đăng nhập của bạn
    
    track_page_view()
    
    today = now().date()
    page_view = PageView.objects.filter(date=today).first()
    visit_count = page_view.count if page_view else 0
    
    customers_count = Customer.objects.count()
    username = request.user.name
    money = request.user.money

    return render(request, 'home.html', {'username':username, 'customer_value': money, "customers_count": customers_count, 'visit_count': visit_count})

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

