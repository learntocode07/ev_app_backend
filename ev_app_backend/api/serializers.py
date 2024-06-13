# api/serializers.py
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)  # You should hash passwords in a real app

class DeviceSerializer(serializers.Serializer):
    device_serial_number = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    city = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)
    pincode = serializers.CharField(max_length=10)
    status = serializers.BooleanField()
    base_price = serializers.FloatField()
    unit_price = serializers.FloatField()
    account_number = serializers.CharField(max_length=100)
    account_name = serializers.CharField(max_length=100)

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)

class TransactionSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    user_id = serializers.CharField(max_length=100)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    charge_start_value = serializers.FloatField()
    charge_end_value = serializers.FloatField()
