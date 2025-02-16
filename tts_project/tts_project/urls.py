"""
URL configuration for tts_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("admin/", admin.site.urls),  
    path("", views.get_home, name='home'),
    
    # path("test/", views.test, name='test'),
    path("submit-input/", views.submit_input, name='submit_input'),  # Xử lý AJAX for
    
    path("index/", views.get_index, name='index'),
    path("instruction/", views.get_instruction, name='instruction'),
    path("money/", views.get_money, name='money'),
    path("payments/", views.get_payments, name='payments'),
    path("profile/", views.get_profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path("history_use/", views.get_history_use, name='history_use'),
    path("history_buy/", views.get_history_buy, name='history_buy'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),  
    path('buy_package/', views.buy_package, name='buy_package'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.CustomPasswordResetView.as_view(template_name='password_reset/password_reset.html'), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(template_name='password_reset/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'), name='password_reset_complete'),
]
