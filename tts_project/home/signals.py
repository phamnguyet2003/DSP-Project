from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from .models import Customer, Wallet, Subscription, Package
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now

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

@receiver(post_migrate)
def check_and_update_subscriptions(sender, **kwargs):
    print('🔄 Signal check_and_update_subscriptions is running...')  # Kiểm tra signal có chạy không
    today = now().date()
    expired_subs = Subscription.objects.filter(end_date__lt=today, status=True)
    count = expired_subs.update(status=False)
    print(f"✅ Updated {count} expired subscriptions to inactive.")
