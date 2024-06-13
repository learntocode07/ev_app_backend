# myapp/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from pymongo import MongoClient
import uuid

# client = MongoClient(settings.MONGO_DB_SETTINGS['host'], settings.MONGO_DB_SETTINGS['port'])
client = MongoClient(settings.MONGO_DB_URI)
db = client[settings.MONGO_DB_SETTINGS['db']]
tokens_collection = db['tokens']
users_collection = db['users']

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None
        
        token_data = tokens_collection.find_one({"token": token})
        if not token_data:
            raise AuthenticationFailed('Invalid token')

        user = users_collection.find_one({"_id": token_data['user_id']})
        if not user:
            raise AuthenticationFailed('User not found')
        
        return (user, token)
    
    @staticmethod
    def generate_token(user_id):
        token = str(uuid.uuid4())
        tokens_collection.insert_one({"token": token, "user_id": user_id})
        return token
