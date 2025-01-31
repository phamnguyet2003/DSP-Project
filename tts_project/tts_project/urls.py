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
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.get_home, name='home'),
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
]
