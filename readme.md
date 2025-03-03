# DSP-Project

## Giới thiệu
Đây là một ứng dụng Django sử dụng Text-to-Speech (TTS) để chuyển đổi văn bản thành giọng nói.

## Cài đặt và chạy dự án

```sh
Nếu bạn muốn dùng chạy local, nhớ thiết lập biến môi trường:
- SECRET_KEY: Secret key của Django 
- EMAIL_PASS, EMAIL_USER: Mật khẩu và gmail của mail doanh nghiệp (phục vụ gửi mail đặt lại mật khẩu) 
- PASSWORD_DB_PostgreSQL: Password connect vào db (sửa phần config DATABASES trong settings)
```

### 1. Kích hoạt môi trường ảo
```sh
myenv\Scripts\activate
```

### 2. Cài đặt môi trường
```sh
pip install -r requirements.txt
```

### 3. Vào thư mục Project
```sh
cd tts_project
```

### 4. Migrate
```sh
python manage.py makemigrations
python manage.py migrate
```

### 5. Chạy ứng dụng
```sh
python manage.py runserver
```