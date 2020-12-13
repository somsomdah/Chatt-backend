from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status,response,viewsets,permissions
from django.contrib.auth import logout
from rest_framework.decorators import action
from .serializers import *
from .models import *
from .utils import *


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    serializer_class=UserSerializer
    queryset=User.objects.all()

class AuthViewSet(viewsets.GenericViewSet):
    permissions_classes=[permissions.AllowAny]
    serializer_class=EmptySerializer
    serializer_classes={
        'login':UserLoginSerializer,
        'register':UserSerializer,
        'change_password':PasswordChangeSerializer
    }

    @action(methods=['post'],detail=False,url_path='login')
    def login(self,request):
        serializer=self.get_serializer(data=request.data) #request.data인 username과 password 받아와서 인스턴스 생성
        serializer.is_valid(raise_exception=True)
        user=get_and_authenticate_user(**serializer.validated_data) # user instance
        # user=get_and_authenticate_user(request.data['username'],request.data['password'])
        # serializer.validated_data -> 원래 데이터
        # serializer.data -> 바뀐 데이터
        data=AuthUserSerializer(user).data # serialize한 데이터
        return response.Response(data=data,status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False,url_path='register')
    def register(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=create_user_account(**serializer.validated_data)
        data=AuthUserSerializer(user).data
        return response.Response(data=data,status=status.HTTP_201_CREATED)

    # 이거 안 됨
    @action(methods=['post'],detail=False,url_path='logout')
    def logout(self,request): # EmptySerializer 사용
        #request.user.auth_token.delete()
        logout(request)
        data={'sucsess':True}
        return response.Response(data=data,status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False,url_path='change-password',permissions_classes=[permissions.IsAuthenticated])
    def change_password(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

    def get_queryset(self):
        pass






