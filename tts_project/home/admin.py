from django.contrib import admin
from .models import *

from django.contrib import admin
from .models import Wallet, Customer

class WalletAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_date', 'value')  # Hiển thị cột trong bảng admin
    search_fields = ['customer__name']  # Cho phép tìm kiếm theo tên khách hàng
    autocomplete_fields = ['customer']  # Bật tính năng autocomplete

admin.site.register(Wallet, WalletAdmin)

class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email', 'phone']  # Cho phép tìm kiếm theo tên, email, số điện thoại

admin.site.register(Customer, CustomerAdmin)

# admin.site.register(Customer)
admin.site.register(Package)
admin.site.register(Subscription)
# admin.site.register(Wallet)
admin.site.register(Payment)
admin.site.register(History)
