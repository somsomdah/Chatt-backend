from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone=models.CharField(max_length=20)
    location_gu=models.CharField(max_length=20,null=True,blank=True)
    location_dong=models.CharField(max_length=20,null=True,blank=True)
    note=models.TextField(null=True,blank=True)

    def __str__(self):
        return "{}{} : {} : {}구 {}동".format(self.last_name,self.first_name,self.username,self.location_gu,self.location_dong)


class Teacher(models.Model):
    image=models.ImageField(null=True,upload_to='image')
    name=models.CharField(max_length=20)
    phone=models.CharField(max_length=20)
    information=models.TextField()
    career1=models.CharField(max_length=100,null=True,blank=True)
    career2=models.CharField(max_length=100,null=True,blank=True)
    career3 = models.CharField(max_length=100,null=True,blank=True)
    career4 = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class RelatedLocation(models.Model):
    teacher=models.ForeignKey('Teacher',on_delete=models.CASCADE, related_name='related_locations')
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
        return "{} : {} : {}{} : (남은횟수){} : (유효성){}".format(self.course.category, self.course.name,self.student.last_name,self.student.first_name,
                                                 self.left_count,self.valid)

class Record(models.Model):
    enrollment=models.ForeignKey('Enrollment',on_delete=models.CASCADE)
    date=models.DateField()
    content=models.ImageField()

    def __str__(self):
        return "{} : {} : {}{}".format(self.date,self.enrollment.course.name,
                                       self.enrollment.student.last_name,self.enrollment.student.first_name)


class Course(models.Model):
    teacher=models.ForeignKey('Teacher',on_delete=models.CASCADE,related_name='courses')
    name=models.CharField(max_length=30)
    category=models.CharField(max_length=30)
    count=models.PositiveIntegerField(default=4)
    duration=models.PositiveIntegerField(default=28)
    information=models.TextField()

    def __str__(self):
        return "{} : {}".format(self.teacher.name,self.name)


class CourseTime(models.Model):
    course=models.ForeignKey('Course',on_delete=models.CASCADE,related_name='course_times')
    enrollment=models.ForeignKey('Enrollment',null=True,blank=True,on_delete=models.CASCADE,related_name='course_times')
    day=models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(6)])
    time=models.PositiveIntegerField(validators=[MinValueValidator(6),MaxValueValidator(22)])
    reserved=models.BooleanField(default=False)
    valid=models.BooleanField(default=True)

    def __str__(self):
        return "{} : {} : {} : {}".format(self.course.name,self.day,self.time,self.valid)

class CourseDetail(models.Model):
    course=models.ForeignKey('Course',on_delete=models.CASCADE,related_name='course_details')
    week=models.PositiveIntegerField()
    content=models.TextField()

    def __str__(self):
        return '{} : {} : {}'.format(self.course.name,self.week,self.content)


