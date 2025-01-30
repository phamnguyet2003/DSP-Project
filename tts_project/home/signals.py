from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer, Wallet, Subscription, Package
from django.utils import timezone
from datetime import timedelta

@receiver(post_save, sender=Customer)
def create_wallet_and_subscription(sender, instance, created, **kwargs):
    if created:
        # Tạo Subscription với ID_Pack=1 và Active=1 (Subscription sẽ phải được liên kết với Package)
        try:
            package = Package.objects.get(id=1)  # Lấy Package với ID=1, bạn có thể điều chỉnh theo yêu cầu
            # Tạo Subscription với start_date và end_date theo yêu cầu (ví dụ: trong 30 ngày)
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=30)
            subscription = Subscription.objects.create(
                customer=instance,
                package=package,
                start_date=start_date,
                end_date=end_date,
                status=True  # Active = 1
            )
        except Package.DoesNotExist:
            print("Package with ID=1 does not exist.")
