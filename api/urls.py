from rest_framework import routers
from .views import *


router=routers.DefaultRouter()

router.register(r'user',UserViewSet)
router.register(r'enrollment',EnrollmentViewSet)
router.register(r'course',CourseViewSet)

urlpatterns=router.urls


