from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status,response,viewsets,permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import login,logout
from rest_framework.decorators import action
from .serializers import *
from .models import *
from .utils import *


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    serializer_class=UserSerializer
    queryset=User.objects.all()
    permissions_classes=[permissions.IsAuthenticated]
    serializer_classes={
        'login':UserLoginSerializer,
        'change_password':PasswordChangeSerializer
    }


    @action(methods=['post'],detail=False,url_path='login',permissions_classes=[permissions.AllowAny])
    def login(self,request):
        serializer=self.get_serializer(data=request.data) #request.data인 username과 password 받아와서 인스턴스 생성
        serializer.is_valid(raise_exception=True)
        user=get_and_authenticate_user(**serializer.validated_data) # user instance
        # user=get_and_authenticate_user(request.data['username'],request.data['password'])
        # serializer.validated_data -> 원래 데이터
        # serializer.data -> 바뀐 데이터
        login(request,user)
        data=UserSerializer(user).data # serialize한 데이터
        return response.Response(data=data,status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False,url_path='register',permissions_classes=[permissions.AllowAny])
    def register(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=create_user_account(**serializer.validated_data)
        login(request,user) # 회원등록하면서 로그인 기능도 포함
        data=UserSerializer(user).data
        return response.Response(data=data,status=status.HTTP_201_CREATED)


    @action(methods=['get'],detail=False,url_path='logout')
    def logout(self,request):
        logout(request)
        data={'sucsess':"logout successful"}
        return response.Response(data=data,status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False,url_path='change-password')
    def change_password(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    # 방문 가능한 선생님 찾기
    @action(methods=['get'],detail=False,url_path='find-teachers')
    def find_teachers(self,request):

        help='Find teachers who are available to visit the customer'

        gu=request.user.location_gu
        dong=request.user.location_dong

        teacher_ids=RelatedLocation.objects.filter(gu=gu,dong=dong).values_list('teacher_id', flat=True)
        serializer=self.get_serializer(User.objects.filter(id__in=teacher_ids),many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)


    # 자신이 등록한 강좌들 찾기
    @action(methods=['get'],detail=False,url_path='courses')
    def find_courses(self,request):

        help='Find courses that the customer had registered'

        enrollment_qs=request.user.enrollments.all().filter(student_id=request.user.id)
        course_ids=enrollment_qs.values_list('course_id',flat=True)
        serializer=CourseSerializer(Course.objects.filter(id__in=course_ids),many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)


    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()





