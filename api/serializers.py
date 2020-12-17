from rest_framework import serializers
from django.contrib.auth import password_validation

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined', 'groups', 'user_permissions']

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


class RelatedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedLocation
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model=Course
        fields='__all__'


class EmptySerializer(serializers.Serializer):
    pass
