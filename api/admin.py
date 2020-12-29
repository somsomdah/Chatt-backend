from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Teacher)
admin.site.register(RelatedLocation)
admin.site.register(Course)
admin.site.register(CourseTime)
admin.site.register(CourseDetail)
admin.site.register(Enrollment)
admin.site.register(Record)
admin.site.register(Package)
admin.site.register(Appointment)
