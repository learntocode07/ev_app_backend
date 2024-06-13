# api/urls.py
from django.urls import path
from .views import register, login, add_device, delete_device, get_devices, start_charging, stop_charging, add_amount_to_wallet, logout

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('add_device/', add_device, name='add_device'),
    path('delete_device/<str:device_id>/', delete_device, name='delete_device'),
    path('get_devices/', get_devices, name='get_devices'),
    path('start_charging/<str:device_id>/', start_charging, name='start_charging'),
    path('stop_charging/<str:device_id>/', stop_charging, name='stop_charging'),
    path('add_amount_to_wallet/', add_amount_to_wallet, name='add_amount_to_wallet'),
    path('logout/', logout, name='logout'),
]
    