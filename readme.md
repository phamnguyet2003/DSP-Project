```md
# DSP-Project

## Giới thiệu
Đây là một ứng dụng Django sử dụng Text-to-Speech (TTS) để chuyển đổi văn bản thành giọng nói.

## Cài đặt và chạy dự án

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