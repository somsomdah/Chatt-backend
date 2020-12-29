from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework import status,response,viewsets,permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import login,logout
from rest_framework.decorators import action
from django.utils import timezone

from .serializers import *
from .models import *
from .utils import *

import datetime


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    serializer_class=UserSerializer
    queryset=User.objects.all()

    permissions_classes = [permissions.IsAuthenticated, ]
    serializer_classes = {
        'login' : UserLoginSerializer,
        'register':UserSerializer,
        'change_password':PasswordChangeSerializer
    }

    @action(methods=['POST', ], detail=False,url_path='login',permissions_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(**serializer.validated_data)
        data = UserSerializer(user).data
        login(request,user)
        return response.Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False,url_path='register',permissions_classes=[permissions.AllowAny])
    def register(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=create_user_account(**serializer.validated_data)
        data=UserSerializer(user).data
        login(request,user) # 회원가입과 동시에 로그인 가능
        return response.Response(data=data,status=status.HTTP_201_CREATED)

    @action(methods=['get'],detail=False,url_path='logout')
    def logout(self,request):
        logout(request)
        data={"sucsess":"Logout Successful"}
        return response.Response(data=data,status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False,url_path='change-password')
    def change_password(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        data={"success": "Password Changed"}
        return response.Response(data=data,status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()



class CourseViewSet(viewsets.ModelViewSet):
    serializer_class=CourseSerializer
    queryset=Course.objects.all()
    permissions_classes = [permissions.IsAuthenticated, ]
    serializer_classes = {
        'reserve' : CourseReservationSerializer,
        'check_times': CourseTimeSerializer,
    }


    @action(methods=['post'],detail=True,url_path='reserve')
    def reserve(self,request,pk):

        help="Reserve a course, it is different from registering one, the course is registered only after payment"

        course=get_object_or_404(Course,pk=pk)
        day,time,package_count,start_date=request.data["day"],request.data["time"],request.data["package_count"],request.data["start_date"]
        y,m,d=map(int,start_date.split('-'))
        start_date=datetime.date(y,m,d)
        package_obj=Package.objects.get(count=package_count)
        enrollment=Enrollment.objects.create(user_id=request.user.id,course_id=pk,package_id=package_obj.id,
                                             start_date=start_date,
                                             end_date=start_date+timezone.timedelta(days=package_obj.duration),
                                             left_count=package_obj.count,valid=False,
                                             lesson_day=day,lesson_time=time)
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_time_qs=course.course_times.all()
        course_time_obj=course_time_qs.get(day=day,time=time)
        if course_time_obj.valid==False:
            return response.Response({"failed" : "Course Time Already Taken"},status=status.HTTP_400_BAD_REQUEST)
        course_time_obj.enrollment_id=enrollment.id
        course_time_obj.save()

        return response.Response(EnrollmentSerializer(enrollment).data,status=status.HTTP_201_CREATED)

    @action(methods=['get'],detail=True,url_path='times')
    def check_times(self,request,pk):
        help="Get course times of a specific course"

        course=get_object_or_404(Course,pk=pk)
        course.course_times.all().filter(enrollment__end_date__lt=timezone.now().date()).update(valid=True,enrollment_id=None)
        serializer=self.get_serializer(course.course_times.all(),many=True)
        return response.Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'],detail=False,url_path='availables')
    def check_availables(self,request):
        help='Get courses that are available for the user based on the location'

        gu=request.user.location_gu
        dong=request.user.location_dong

        teacher_ids=RelatedLocation.objects.filter(gu=gu,dong=dong).values_list('teacher_id', flat=True)
        serializer=CourseSerializer(Course.objects.filter(teacher_id__in=teacher_ids),many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'],detail=False,url_path='enrollments')
    def check_enrollments(self,request):

        help='Check courses that the customer had registered'

        enrollments=Enrollment.objects.filter(user_id=request.user.id)
        enrollments.filter(end_date__lt=timezone.now().date()).update(valid=False)
        serializer=EnrollmentSerializer(enrollments,many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'],detail=False,url_path='weekly')
    def show_by_week(self,request):
    # 로그인 안되어있을 때에는 모든 강의 리스트업 하도록
        result={}
        #if request.user.is_authenticated():
        for i in range(7):
            courses=Course.objects.filter(course_times__day__exact=i,
                                        teacher__related_locations__dong=request.user.location_dong,
                                        teacher__related_locations__gu=request.user.location_gu)

            for course in courses:
                expired_enrollments=course.enrollments.all().filter(end_date__lt=timezone.now().date())
                expired_enrollments.update(valid=False)
                expired_enrollments_id=expired_enrollments.values_list('id',flat=True)
                course.course_times.all().filter(enrollment_id__in=expired_enrollments_id).update(valid=True,enrollment_id=None)

            result[i]=CourseAbstractSerializer(courses,many=True).data
        return response.Response(result,status=status.HTTP_200_OK)


    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class=EnrollmentSerializer
    queryset=Enrollment.objects.all()
