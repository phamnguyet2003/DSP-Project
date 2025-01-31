from django.apps import AppConfig

class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    
    def ready(self):
        import home.signals  # Thay 'yourapp' bằng tên ứng dụng của bạn
        

