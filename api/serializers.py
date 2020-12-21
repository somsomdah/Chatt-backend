from rest_framework import serializers
from django.contrib.auth import password_validation
from django.core.validators import MaxValueValidator, MinValueValidator


from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined', 'groups', 'user_permissions']

    def create(self, validated_data):
        '''
        user = User(username=validated_data["username"],phone=validated_data["phone"],
                    location_gu=validated_data["location_gu"],location_dong=validated_data["location_dong"],
                    email=validated_data["email"],first_name=validated_data["first_name"],last_name=validated_data["last_name"])
        '''
        user=User.objects.create_user(**validated_data)
        #user.set_password(validated_data['password'])
        #user.save()
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
    username = serializers.CharField(max_length=120,required=True)
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

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=Teacher
        fields="__all__"


class RelatedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedLocation
        fields = '__all__'


class CourseTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model=CourseTime
        fields="__all__"

class EnrollmentSerializer(serializers.ModelSerializer):
    course=serializers.SerializerMethodField()
    times=serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = '__all__'

    def get_times(self,obj):
        serializer=CourseTimeSerializer(CourseTime.objects.filter(enrollment_id=obj.id),many=True)
        return serializer.data

    def get_course(self,obj):
        serializer=CourseSerializer(Course.objects.get(id=obj.course_id))
        return serializer.data


class CourseDetailSerilizer(serializers.ModelSerializer):
    class Meta:
        model=CourseDetail
        fields='__all__'

class CourseSerializer(serializers.ModelSerializer):

    teacher=serializers.SerializerMethodField()
    course_details=CourseDetailSerilizer(many=True)
    course_times=CourseTimeSerializer(many=True)

    class Meta:
        model=Course
        fields="__all__"

    def get_teacher(self,obj):
        return TeacherSerializer(Teacher.objects.get(id=obj.teacher_id)).data

class CourseRegisterSerializer(serializers.Serializer):
    day=serializers.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(6)])
    time=serializers.IntegerField(validators=[MinValueValidator(6),MaxValueValidator(22)])

class EmptySerializer(serializers.Serializer):
    pass
