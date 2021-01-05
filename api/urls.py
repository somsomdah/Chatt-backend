from rest_framework import routers
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

from .views import *


router=routers.DefaultRouter()

router.register(r'user',UserViewSet)
router.register(r'enrollment',EnrollmentViewSet)
router.register(r'teacher',TeacherViewSet)
router.register(r'course',CourseViewSet)
router.register(r'appointment',AppointmentViewSet)

urlpatterns = [
    path('user/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]


