# api/views.py
import bcrypt
from django.conf import settings
from pymongo import MongoClient
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from datetime import datetime
from .serializers import UserSerializer, DeviceSerializer
from .authentication import CustomTokenAuthentication

# client = MongoClient(settings.MONGO_DB_SETTINGS['host'], settings.MONGO_DB_SETTINGS['port'])
client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_SETTINGS['db']]
users_collection = db['users']
devices_collection = db['devices']
tokens_collection = db['tokens']

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = users_collection.find_one({"username": serializer.data['username']})
        if user:
            return Response({"message": "Duplicate username!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        hashed_password = bcrypt.hashpw(serializer.validated_data['password'].encode('utf-8'), bcrypt.gensalt())
        user_data = serializer.data
        user_data['password'] = hashed_password.decode('utf-8')  # Convert to string for storage
        users_collection.insert_one(user_data)
        # users_collection.insert_one(serializer.data)
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = users_collection.find_one({"username": username})
    # if user:
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        token = CustomTokenAuthentication.generate_token(user['_id'])
        return Response({"token": token}, status=status.HTTP_200_OK)
    return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
def add_device(request):
    # serializer = DeviceSerializer(data=request.data)
    # if serializer.is_valid():
    #     devices_collection.insert_one(serializer.data)
    #     return Response({"message": "Device added successfully"}, status=status.HTTP_201_CREATED)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user_id = request.user['_id']
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        device_data = serializer.data
        device_data['user_id'] = user_id  # Associate device with the user
        devices_collection.insert_one(device_data)
        return Response({"message": "Device added successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([CustomTokenAuthentication])
def delete_device(request, device_id):
    result = devices_collection.delete_one({"device_id": device_id})
    if result.deleted_count:
        return Response({"message": "Device deleted successfully"}, status=status.HTTP_200_OK)
    return Response({"message": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([CustomTokenAuthentication])
def get_devices(request):
    devices = list(devices_collection.find())
    for device in devices:
        device['_id'] = str(device['_id'])  # Convert ObjectId to string for JSON serialization
    return Response(devices, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
def start_charging(request, device_id):
    result = devices_collection.update_one(
        {"device_id": device_id}, 
        {"$set": {
            "status": "on",
            "start_time": datetime.now()
            }
        })
    if result.matched_count:
        return Response({"message": "Device turned on successfully"}, status=status.HTTP_200_OK)
    return Response({"message": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
def stop_charging(request, device_id):
    result = devices_collection.update_one({"device_id": device_id}, {"$set": {"status": "off"}})
    if result.matched_count:
        return Response({"message": "Device turned off successfully"}, status=status.HTTP_200_OK)
    return Response({"message": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
def add_amount_to_wallet(request):
    user_id = request.user['_id']
    amount = request.data.get('amount')
    if amount is None or not isinstance(amount, (int, float)):
        return Response({"message": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

    result = users_collection.update_one({"_id": user_id}, {"$inc": {"wallet": amount}})
    if result.matched_count:
        return Response({"message": "Amount added to wallet successfully"}, status=status.HTTP_200_OK)
    return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
def logout(request):
    token = request.auth
    result = tokens_collection.delete_one({"token": token})
    if result.deleted_count:
        return Response({"message": "Logout successful, token cleared"}, status=status.HTTP_200_OK)
    return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)