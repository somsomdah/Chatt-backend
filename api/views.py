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
        user = get_and_authenticate_user(request.data["username"],request.data["password"])
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

    @action(methods=['get'],detail=False,url_path='find-teachers')
    def find_teachers(self,request):

        help='Find teachers who are available to visit the customer'

        gu=request.user.location_gu
        dong=request.user.location_dong

        teacher_ids=RelatedLocation.objects.filter(gu=gu,dong=dong).values_list('teacher_id', flat=True)
        serializer=self.get_serializer(Teacher.objects.filter(id__in=teacher_ids),many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'],detail=False,url_path='enrollments')
    def check_enrollments(self,request):

        help='Check courses that the customer had registered'

        enrollments=Enrollment.objects.filter(student_id=request.user.id)
        serializer=EnrollmentSerializer(enrollments,many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)

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
        'register' : CourseRegisterSerializer,
    }

    # 여기 확인하기
    @action(methods=['post'],detail=True,url_path='register')
    def register(self,request,pk):
        course=Course.objects.get_object_or_404(pk=pk)
        enrollment=Enrollment.objects.create(student_id=request.user.id,course_id=pk,
                                             start_date=timezone.now().date(),end_date=start_date+timezone.timedelta(time=course.duration),
                                             left_count=course.count,valid=True)
        serializer=self.get_serializer(request.data)
        serializer.is_valid(raise_exception=True)

        day,time=serializer.validated_data

        course_time_qs=course.course_times.all()
        course_time_obj=course_time_qs.get_object_or_404(day=day,time=time)
        course_time_obj.valid=0
        course_time_obj.enrollment_id=enrollment.id


    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class=EnrollmentSerializer
    queryset=Enrollment.objects.all()

#    @action(methods=['get'],detail=False,url_path)