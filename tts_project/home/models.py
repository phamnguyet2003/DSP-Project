from django.db import models
from django.contrib.auth.models import AbstractUser

# Customer model: Lưu thông tin khách hàng
class Customer(AbstractUser):
    name = models.CharField(max_length=150, blank=True, null=True)  # Thêm blank=True, null=True để tránh lỗi bắt buộc
    phone = models.CharField(max_length=15, blank=True, null=True)

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
        return f"Subscription for {self.customer.name} to {self.package.language}"


# Payment model: Lưu thông tin thanh toán
class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment of {self.value} for {self.customer.name}"


# History model: Lưu thông tin sử dụng dịch vụ của khách hàng
class History(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField()
    input_data = models.TextField()
    output_data = models.TextField()

    def __str__(self):
        return f"History for {self.customer.name} on {self.date}"


# Wallet model: Lưu số dư ví của khách hàng
class Wallet(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    old_value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Wallet for {self.customer.name}"
