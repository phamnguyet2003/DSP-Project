from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Package)
admin.site.register(Subscription)
admin.site.register(Wallet)
admin.site.register(Payment)
admin.site.register(History)
