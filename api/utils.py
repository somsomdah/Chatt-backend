from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q,F
from rest_framework import serializers
#import logging
from .models import *

#logger=logging.getLogger(__name__)

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
                                  **extra_fields
                                  )
    return user

def expire_enrollments():
    enrollments=Enrollment.objects.filter(Q(end_date__lt=timezone.now().date())|Q(left_count__lte=0))
    # for enrollment in enrollments:
    #    print(enrollment)
    enrollments.update(valid=False)
    expired_enrollment_ids=enrollments.values_list('id',flat=True)
    CourseTime.objects.filter(enrollment_id__in=expired_enrollment_ids).update(valid=True,enrollment_id=None)


def validate_coursetimes():
    valid_enrollment_ids=Enrollment.objects.filter(valid=True).values_list('id',flat=True)
    for id in valid_enrollment_ids:
        CourseTime.objects.filter(enrollment_id=id).update(valid=False)

