from django.contrib import admin
from .models import *

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    model=User
    list_display = ['username','last_name','first_name','location_gu','location_dong','note']

class TeacherAdmin(admin.ModelAdmin):
    model=Teacher
    list_display = ['name','nickname','phone']

class CourseAdmin(admin.ModelAdmin):
    model=Course
    ordering=("teacher__id",)
    list_display = ['teacher','name']

class CourseTimeAdmin(admin.ModelAdmin):
    model = CourseTime
    ordering = ("course__id", 'day', 'time')
    list_display = ['teacher','course_name','day','time','taken','enrollment_username']
    list_filter=['taken','course']
    #list_editable = ['day','time']

    def teacher(self,obj):
        return obj.course.teacher
    def course_name(self,obj):
        return obj.course.name
    def enrollment_username(self,obj):
        if obj.enrollment is None:
            return None
        return obj.enrollment.user.username

class CourseDetailAdmin(admin.ModelAdmin):
    model=CourseDetail
    ordering=('course__id','index')
    list_display = ['course','index','content']
    list_filter = ['course']

class RelatedLocationAdmin(admin.ModelAdmin):
    model=RelatedLocation
    ordering=("teacher__id",)
    list_display=['teacher','gu','dong']
    list_filter=['teacher','gu','dong']
    #list_editable = ['gu','dong']

class EnrollmentAdmin(admin.ModelAdmin):
    model=Enrollment
    ordering=['user__id']
    list_display = ['username','course_category','course_name','lesson_day','lesson_time','valid','paid']
    list_filter = ['user','valid','paid']
    list_editable = ['paid']

    def username(self,obj):
        return obj.user.username
    def course_category(self,obj):
        return obj.course.category
    def course_name(self,obj):
        return obj.course.name


class RecordAdmin(admin.ModelAdmin):
    model=Record
    ordering=('enrollment__id',)
    list_display=['username','course','content','date']
    list_filter=['enrollment']

    def username(self,obj):
        return obj.enrollment.user.username
    def course(self,obj):
        return obj.enrollment.course.name

class PackageAdmin(admin.ModelAdmin):
    model=Package
    ordering=('count',)
    list_display = ['count','price','duration']

class AppointmentAdmin(admin.ModelAdmin):
    model=Appointment
    ordering=('date','time')
    list_display = ['date','time','username','completed']
    list_filter = ['date','user','completed']
    list_editable = ['completed']

    def username(self,obj):
        return obj.user.username


admin.site.register(User,UserAdmin)
admin.site.register(Teacher,TeacherAdmin)
admin.site.register(RelatedLocation,RelatedLocationAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(CourseTime,CourseTimeAdmin)
admin.site.register(CourseDetail,CourseDetailAdmin)
admin.site.register(Enrollment,EnrollmentAdmin)
admin.site.register(Record,RecordAdmin)
admin.site.register(Package,PackageAdmin)
admin.site.register(Appointment,AppointmentAdmin)
