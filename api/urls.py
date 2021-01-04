from rest_framework import routers
from .views import *


router=routers.DefaultRouter()

router.register(r'user',UserViewSet)
router.register(r'enrollment',EnrollmentViewSet)
router.register(r'teacher',TeacherViewSet)
router.register(r'course',CourseViewSet)
router.register(r'appointment',AppointmentViewSet)

urlpatterns=router.urls


