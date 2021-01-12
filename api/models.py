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
        return "{} | {}{} | {}구 {}동".format(self.username,self.last_name,self.first_name,self.location_gu,self.location_dong)


class Teacher(models.Model):
    image=models.ImageField(null=True,blank=True,upload_to='media')
    name=models.CharField(max_length=20)
    nickname=models.CharField(max_length=40)
    phone=models.CharField(max_length=20)
    information=models.TextField()
    career1=models.CharField(max_length=100,null=True,blank=True)
    career2=models.CharField(max_length=100,null=True,blank=True)
    career3 = models.CharField(max_length=100,null=True,blank=True)
    career4 = models.CharField(max_length=100, null=True, blank=True)
    instagram=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return "{}".format(self.name)


class RelatedLocation(models.Model):
    teacher=models.ForeignKey('Teacher',on_delete=models.CASCADE, related_name='related_locations')
    gu=models.CharField(max_length=20)
    dong=models.CharField(max_length=20)

    class Meta:
        order_with_respect_to='teacher'

    def __str__(self):
        return "{} | {}구 {}동".format(self.teacher.name,self.gu,self.dong)

class Package(models.Model):
    price=models.PositiveIntegerField()
    duration=models.PositiveIntegerField()
    count=models.PositiveIntegerField()
    def __str__(self):
        return "횟수 : {} | 가격 : {} | 기한 : {}".format(self.count,self.price,self.duration)

class Enrollment(models.Model):
    user=models.ForeignKey('User',on_delete=models.CASCADE, related_name='enrollments')
    course=models.ForeignKey('Course',on_delete=models.SET_NULL,null=True,blank=True, related_name='enrollments')
    package=models.ForeignKey('Package',on_delete=models.SET_NULL,null=True,blank=True,related_name='enrollments')

    start_date=models.DateField(default=None,null=True,blank=True)
    end_date=models.DateField(default=None,null=True,blank=True)

    lesson_day=models.PositiveIntegerField(choices=((0,'mon'),(1,'tue'),(2,'wed'),(3,'thu'),(4,'fri'),(5,'sat'),(6,'sun')))
    lesson_time=models.PositiveIntegerField(validators=[MinValueValidator(6),MaxValueValidator(22)],null=True,blank=True)

    left_count=models.PositiveIntegerField(default=4)
    paid=models.BooleanField(default=False)
    valid=models.BooleanField(default=True) # valid == false means the enrollment is expired

    class Meta:
        order_with_respect_to='user'

    def __str__(self):
        return "{} | {} | {} | {} {} |  (남은횟수){} | (유효성){} | (결제){}".format(self.course.category, self.course.name,
                                                                     self.user.username,
                                                                     self.lesson_day,self.lesson_time,
                                                                     self.left_count,self.valid,self.paid)

class Record(models.Model):
    enrollment=models.ForeignKey('Enrollment',on_delete=models.CASCADE,related_name='records')
    date=models.DateField()
    content=models.ImageField(null=True,blank=True,upload_to='media')

    class Meta:
        order_with_respect_to='enrollment'

    def __str__(self):
        return "{} | {} | {}".format(self.enrollment.course.name,self.enrollment.user.username,self.date,)


class Course(models.Model):
    teacher=models.ForeignKey('Teacher',on_delete=models.CASCADE,related_name='courses')
    name=models.CharField(max_length=30)
    category=models.CharField(max_length=30,default='필라테스')
    is_visit=models.BooleanField(default=True)
    information=models.TextField()
    image1=models.ImageField(null=True,blank=True,upload_to='media')
    image2=models.ImageField(null=True,blank=True,upload_to='media')
    image3=models.ImageField(null=True,blank=True,upload_to='media')
    tag1=models.CharField(max_length=100,null=True,blank=True)
    tag2 = models.CharField(max_length=100, null=True, blank=True)
    tag3 = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        order_with_respect_to='teacher'

    def __str__(self):
        return "{} | {}".format(self.teacher.name,self.name)


class CourseTime(models.Model):
    course=models.ForeignKey('Course',on_delete=models.CASCADE,related_name='course_times')
    enrollment=models.OneToOneField('Enrollment',null=True,blank=True,on_delete=models.CASCADE,related_name='course_time')
    day=models.PositiveIntegerField(choices=((0,'mon'),(1,'tue'),(2,'wed'),(3,'thu'),(4,'fri'),(5,'sat'),(6,'sun')))
    time=models.PositiveIntegerField(validators=[MinValueValidator(6),MaxValueValidator(22)])
    taken=models.BooleanField(default=False)

    class Meta:
        order_with_respect_to='course'

    def __str__(self):
        return "{} | {} | {} | {}".format(self.course.name,self.day,self.time,self.taken)

class CourseDetail(models.Model):
    course=models.ForeignKey('Course',on_delete=models.CASCADE,related_name='course_details')
    index=models.PositiveIntegerField()
    content=models.TextField()

    class Meta:
        ordering=['course__id','index']

    def __str__(self):
        return '{} | {} | {}'.format(self.course.name,self.index,self.content)

class Appointment(models.Model):
    user=models.ForeignKey('User',on_delete=models.CASCADE,related_name='user')
    date=models.DateField()
    time=models.PositiveIntegerField()
    level=models.PositiveIntegerField(choices=((1,'beginner'),(2,'intermediate'),(3,'advanced')))
    note=models.TextField(blank=True,null=True)
    completed=models.BooleanField(default=False)

    class Meta:
        ordering=['date','time']

    def __str__(self):
        return "{} | {} | {} | {}".format(self.date,self.time,self.user.username,self.completed)

