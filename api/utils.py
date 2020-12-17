from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *

def get_and_authenticate_user(username, password):
    user = authenticate(username=username, password=password)
    if user is None:
        raise serializers.ValidationError("Invalid email/password")
    return user

def create_user_account(username,password,first_name,last_name,email,phone,location_gu,location_dong,**extra_fields):
    user =User.objects.create_user(username=username,password=password,
                                  first_name=first_name,last_name=last_name,
                                  email=email,phone=phone,
                                  location_gu=location_gu,location_dong=location_dong,
                                  **extra_fields
                                  )
    return user