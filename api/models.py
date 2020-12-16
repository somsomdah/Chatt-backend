from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # photo=models.ImageField(null=True)
    phone=models.CharField(max_length=20)
    role=models.CharField(max_length=1,choices=(('C','Customer'),('T','Teacher'),('S','Staff')),default='C')
    location_gu=models.CharField(max_length=20)
    location_dong=models.CharField(max_length=20)
    information=models.TextField(null=True,blank=True)


class RelatedLocation(models.Model):
    teacher=models.ForeignKey('User',on_delete=models.CASCADE, related_name='related_locations')
    gu=models.CharField(max_length=20)
    dong=models.CharField(max_length=20)

    def __str__(self):
        return "{} : {}구 {}동".format(self.teacher.username,self.gu,self.dong)


class Enrollment(models.Model):
    student=models.ForeignKey('User',on_delete=models.CASCADE, related_name='enrollments')
    course=models.ForeignKey('Course',on_delete=models.CASCADE, related_name='enrollments')
    start_date=models.DateField(default=timezone.now().date())
    end_date=models.DateField(default=timezone.now().date()+timezone.timedelta(days=28))
    left_count=models.PositiveIntegerField(default=4)
    valid=models.BooleanField(default=True)

    def __str__(self):
        return "{} {} : {} : {}".format(self.student.first_name,self.student.last_name,
                                      self.course.category, self.course.name)


class ClassTime(models.Model):
    enrollment=models.ForeignKey('Enrollment',on_delete=models.CASCADE,related_name='class_times')
    day=models.CharField(max_length=10,choices=(('Mon','Monday'),('Tue','Tuesday'),('Wed','Wednesday'),('Thu','Thursday'),
                                                ('Fri','Friday'),('Sat','Saturday'),('Sun','Sunday')))
    time=models.PositiveIntegerField(validators=[MinValueValidator(6),MaxValueValidator(22)])


class Course(models.Model):
    teacher=models.ForeignKey('User',on_delete=models.CASCADE,related_name='courses')
    name=models.CharField(max_length=30)
    category=models.CharField(max_length=30)
    count=models.PositiveIntegerField(default=4)
    duration=models.PositiveIntegerField(default=28)
    information=models.TextField()
