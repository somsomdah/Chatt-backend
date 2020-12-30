from rest_framework import serializers
from django.contrib.auth import password_validation
from django.core.validators import MaxValueValidator, MinValueValidator


from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined', 'groups', 'user_permissions']

    def create(self, validated_data):
        user=User.objects.create_user(**validated_data)
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
    username = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True)


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

class TeacherSerializer(serializers.ModelSerializer):
    related_locations=RelatedLocationSerializer(many=True)
    class Meta:
        model=Teacher
        fields="__all__"


class CourseTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model=CourseTime
        fields="__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'


class CourseDetailSerilizer(serializers.ModelSerializer):
    class Meta:
        model=CourseDetail
        fields='__all__'


class CourseSerializer(serializers.ModelSerializer):
    teacher=TeacherSerializer(many=False)
    course_details=CourseDetailSerilizer(many=True)
    course_times=CourseTimeSerializer(many=True)

    class Meta:
        model=Course
        fields="__all__"


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Package
        fields="__all__"


class CourseReservationSerializer(serializers.Serializer):
    day=serializers.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(6)])
    time=serializers.IntegerField(validators=[MinValueValidator(6),MaxValueValidator(22)])
    package_count=serializers.IntegerField()
    start_date=serializers.DateField()

class CourseAbstractSerializer(serializers.ModelSerializer):
    teacher=TeacherSerializer()
    class Meta:
        model=Course
        fields="__all__"


class EmptySerializer(serializers.Serializer):
    pass
