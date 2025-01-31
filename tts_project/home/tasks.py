from datetime import datetime
from .models import Subscription

def update_subscription_status():
    today = datetime.today().date()
    subscriptions = Subscription.objects.filter(end_date__lt=today, status=True)
    
    for subscription in subscriptions:
        subscription.status = False
        subscription.save()

    return f"Updated {subscriptions.count()} subscriptions."
