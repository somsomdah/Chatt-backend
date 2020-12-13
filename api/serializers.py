from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import password_validation

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['last_login', 'is_superuser', 'is_staff', 'date_joined', 'groups', 'user_permissions']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        user = User.objects.filter(username=value)
        if user:
            raise serializers.ValidationError("Username already taken")
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=120)
    password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Current password does not match')
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()  # custom field 정의

    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_superuser', 'is_staff', 'date_joined', 'groups', 'user_permissions']

    def get_auth_token(self, obj):
        token = Token.objects.create(user=obj)
        return token.key


class EmptySerializer(serializers.Serializer):
    pass
