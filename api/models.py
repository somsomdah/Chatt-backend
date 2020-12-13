from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone=models.CharField(max_length=20)
    role=models.CharField(max_length=1,choices=(('C','Customer'),('T','Teacher'),('S','Staff')),default='C')
    location_gu=models.CharField(max_length=20)
    location_dong=models.CharField(max_length=20)
    information=models.TextField(null=True,blank=True)


