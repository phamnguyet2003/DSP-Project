import os
import django
from django.conf import settings

# Đặt biến môi trường để Django biết nơi tìm settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tts_project.settings")

# Khởi tạo Django
django.setup()

# Kiểm tra BASE_DIR
print("BASE_DIR:", settings.MEDIA_ROOT)
