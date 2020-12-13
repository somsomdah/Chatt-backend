from rest_framework import routers
from .views import *


router=routers.DefaultRouter()

router.register(r'user',UserViewSet)
router.register(r'auth',AuthViewSet,basename='auth')

urlpatterns=router.urls
