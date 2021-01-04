from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q,F
from rest_framework import serializers
import datetime
from .models import *


def get_and_authenticate_user(username, password):
    user = authenticate(username=username, password=password)
    if user is None:
        raise serializers.ValidationError("Invalid username/password")
    return user

def create_user_account(username,password,first_name,last_name,email,phone,location_gu,location_dong,**extra_fields):
    user =User.objects.create_user(username=username,password=password,
                                  first_name=first_name,last_name=last_name,
                                  email=email,phone=phone,
                                  location_gu=location_gu,location_dong=location_dong,
                                  **extra_fields)
    return user

def expire_enrollments():
    enrollments=Enrollment.objects.filter(Q(end_date__lt=timezone.now().date())|Q(left_count__lte=0))
    enrollments.update(valid=False,left_count=0)
    expired_enrollment_ids=enrollments.values_list('id',flat=True)
    CourseTime.objects.filter(enrollment_id__in=expired_enrollment_ids).update(taken=False,enrollment_id=None)


def update_enrollment_left_count():
    enrollments=Enrollment.objects.all()

    for enrollment in enrollments:
        start_date=enrollment.start_date
        today=datetime.date.today()
        lesson_time=enrollment.lesson_time
        now_hour=int(datetime.datetime.now().hour)

        if (start_date==today and lesson_time<=now_hour) or start_date<today:
            x=(today-start_date).days
            for i in range(enrollment.package.count):
                if 7*i<=x<7*(i+1):
                    enrollment.left_count=enrollment.package.count-(i+1)
                    enrollment.save()
