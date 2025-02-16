from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

# Customer model: Lưu thông tin khách hàng
class Customer(AbstractUser):
    name = models.CharField(max_length=150, blank=True, null=True)  # Thêm blank=True, null=True để tránh lỗi bắt buộc
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    money = models.IntegerField(default=0)
    REQUIRED_FIELDS = ['name', 'phone']
    def __str__(self):
        return self.username 
# Package model: Lưu thông tin gói sản phẩm
class Package(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=50, default=None)  # Voice, default=None
    duration = models.IntegerField(null=True, blank=True)  # Duration in days, default=None
    number_of_works = models.IntegerField()
    tts = models.TextField()  # Text-to-Speech features, maybe JSON or description
    language = models.CharField(max_length=50)
    voice = models.CharField(max_length=50, null=True, blank=True)  # Voice, default=None
    advanced_customization = models.BooleanField(default=False)
    no_ad = models.BooleanField(default=False)
    cloud_storage = models.IntegerField(null=True, blank=True)  # Cloud storage in GB, default=None

    def __str__(self):
        return f"Package {self.id} - {self.name}"



# Subscription model: Lưu thông tin lịch sử đăng ký
class Subscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.BooleanField(default=True)  # Active or Inactive
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription for {self.customer.name} to {self.package.name}"


# Payment model: Lưu thông tin thanh toán tiền trong hệ thống mà khách hàng dùng mua gói cước
class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, default=1)
    transaction_date = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Payment of {self.value} for {self.customer.name}"


# History model: Lưu thông tin sử dụng dịch vụ của khách hàng
class History(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name="histories")
    timestamp = models.DateTimeField(default=now)  # Ghi lại thời gian chi tiết hơn
    input_text = models.TextField()  # Lưu text đầu vào 10 chữ đầu tiên
    text_file = models.FileField(blank=True, null=True)  # Lưu file audio
    voice_file = models.FileField(upload_to="tts_outputs/", blank=True, null=True)  # Lưu file audio
    package = models.ForeignKey('Package', on_delete=models.SET_NULL, null=True, blank=True)  # Tham chiếu đến bảng Package

    class Meta:
        ordering = ['-timestamp']  # Sắp xếp mới nhất lên đầu
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"History for {self.customer.name} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


# Wallet model: Lưu tiền khách chuyển vào ngân hàng
class Wallet(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(default=now)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """Cập nhật money của Customer khi Wallet được thêm hoặc cập nhật"""
        if self.pk is None:  # Chỉ cập nhật khi tạo mới
            self.customer.money += self.value
            self.customer.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Wallet for {self.customer.username}"
