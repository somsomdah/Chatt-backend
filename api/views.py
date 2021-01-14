from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework import status,response,viewsets,permissions
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import F, Q, Count
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import *
from .models import *
from .utils import *

from datetime import datetime,timedelta,date

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    serializer_class=UserSerializer
    queryset=User.objects.all()

    permissions_classes = [permissions.IsAuthenticated, ]
    serializer_classes = {
        'register':UserRegisterSerializer,
        'change_password':PasswordChangeSerializer
    }

    @action(methods=['get'], detail=False,url_path='information')
    def information(self, request):
        user = request.user
        data = UserSerializer(user).data
        return response.Response(data=data, status=status.HTTP_200_OK)


    @action(methods=['post'],detail=False,url_path='register',permissions_classes=[permissions.AllowAny])
    def register(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user=create_user_account(**serializer.validated_data)
        data=UserSerializer(user).data

        update_enrollment_left_count()
        expire_enrollments()

        return response.Response(data=data,status=status.HTTP_201_CREATED)

        #return response.Response(data={"test":"test"},status=status.HTTP_201_CREATED)



    @action(methods=['post'],detail=False,url_path='logout')
    def logout(self,request):
       refresh_token = request.data["refresh_token"]
       token = RefreshToken(refresh_token)
       token.blacklist()
       data={"sucsess":"Logout Successful"}
       return response.Response(data=data,status=status.HTTP_205_RESET_CONTENT)


    @action(methods=['post'],detail=False,url_path='change-password')
    def change_password(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        data={"success": "Password Changed"}
        return response.Response(data=data,status=status.HTTP_200_OK)


    @action(methods=['get'],detail=False,url_path='check-authentication',permissions_classes=[permissions.AllowAny])
    def check_authentication(self,request):
        print(request)
        if request.user.is_authenticated:
            return response.Response(data={'login':True},status=status.HTTP_200_OK)
        else:
            return response.Response(data={'login':False},status=status.HTTP_200_OK)


    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()



class CourseViewSet(viewsets.ModelViewSet):
    serializer_class=CourseSerializer
    queryset=Course.objects.all().annotate(enrollment_count=Count('enrollments')).order_by('-enrollment_count')
    permissions_classes = [permissions.IsAuthenticated, ]
    serializer_classes = {
        'reserve' : CourseReservationSerializer,
        'check_times': CourseTimeSerializer,
    }


    @action(methods=['post'],detail=True,url_path='reserve')
    def reserve(self,request,pk):
        help='reserve a course'

        #update_enrollment_left_count()
        #expire_enrollments()

        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.is_authenticated:
            return response.Response(data={'failed' : 'User Not Logged In'},status=status.HTTP_401_UNAUTHORIZED)

        course=get_object_or_404(Course,pk=pk)
        day,time,package_count,start_date=request.data["day"],request.data["time"],request.data["package_count"],request.data["start_date"]

        course_time_qs=course.course_times.all().filter(day=day,time=time)
        if not course_time_qs: # 강좌에 해당 시간이 열리지 않았을 때
            return response.Response(data={'failed' : 'Course Time Not Available'},status=status.HTTP_400_BAD_REQUEST)

        course_time_obj=course_time_qs[0]
        if course_time_obj.taken==True: # 강좌의 해당 시간을 "현재" 이미 다른 사람이 쓰고 있을 때
            return response.Response(data={"failed" : "Course Time Already Taken"},status=status.HTTP_400_BAD_REQUEST)

        y,m,d=map(int,start_date.split('-'))
        start_date=date(y,m,d)
        package_obj=Package.objects.get(count=package_count)
        enrollment=Enrollment.objects.create(user_id=request.user.id,course_id=pk,package_id=package_obj.id,
                                             start_date=start_date,
                                             end_date=start_date+timezone.timedelta(days=package_obj.duration),
                                             left_count=package_obj.count,valid=True,paid=False,
                                             lesson_day=day,lesson_time=time)

        course_time_obj.enrollment_id=enrollment.id
        course_time_obj.taken=True
        course_time_obj.save()

        return response.Response(EnrollmentSerializer(enrollment).data,status=status.HTTP_201_CREATED)


    @action(methods=['get'],detail=True,url_path='times')
    def check_times(self,request,pk):
        help="Get course times of a specific course"
        expire_enrollments()

        course=get_object_or_404(Course,pk=pk)
        serializer=self.get_serializer(course.course_times.all(),many=True)
        return response.Response(serializer.data,status=status.HTTP_200_OK)


    @action(methods=['get'],detail=False,url_path='availables')
    def check_availables(self,request):
        help='Get courses that are available for the user based on the location'
        expire_enrollments()

        gu=request.user.location_gu
        dong=request.user.location_dong

        teacher_ids=RelatedLocation.objects.filter(gu=gu,dong=dong).values_list('teacher_id', flat=True)
        serializer=CourseSerializer(Course.objects.filter(teacher_id__in=teacher_ids),many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)


    @action(methods=['get'],detail=False,url_path='weekly')#,permissions_classes=[permissions.AllowAny])
    def show_by_week(self,request):
        help= "Show courses by day of the week"
        expire_enrollments()
        result=dict()

        if request.user.is_authenticated:
            for i in range(7):
                courses=Course.objects.filter(course_times__day__exact=i,
                                            teacher__related_locations__dong=request.user.location_dong,
                                            teacher__related_locations__gu=request.user.location_gu).distinct()
                #=courses.values_list('id', flat=True)

                result[i]=CourseAbstractSerializer(courses,many=True).data

                for course in result[i]:
                    times=""
                    coursetimes=CourseTime.objects.filter(course_id=course['id'],day=i)
                    for coursetime in coursetimes:
                        times+=(str(coursetime.time)+" ")
                    course['times']=times


        else:
            for i in range(7):
                courses=Course.objects.filter(course_times__day__exact=i).distinct()
                #course_ids=courses.values_list('id', flat=True)

                result[i]=CourseAbstractSerializer(courses,many=True).data

                for course in result[i]:
                    times=""
                    coursetimes=CourseTime.objects.filter(course_id=course['id'],day=i)
                    for coursetime in coursetimes:
                        times+=(str(coursetime.time)+" ")
                    course['times']=times

        return response.Response(result,status=status.HTTP_200_OK)


    @action(methods=['get'],detail=False,url_path='populars')
    def show_popular_courses(self,request):
        help="Show three most popular courses based on the count of enrollments"
        expire_enrollments()

        if self.queryset.count()>=3:
            return response.Response(CourseAbstractSerializer(self.queryset[:3],many=True).data)
        else:
            return response.Response(CourseAbstractSerializer(self.queryset,many=True).data)


    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class=EnrollmentSerializer
    queryset=Enrollment.objects.all()
    permissions_classes = [permissions.IsAuthenticated, ]

    @action(methods=['get'],detail=False,url_path='history')
    def show_enrollment_history(self,request):
        if not request.user.is_authenticated:
            return response.Response(data={'failed' : 'User Not Logged In'},status=status.HTTP_401_UNAUTHORIZED)
        update_enrollment_left_count()
        expire_enrollments()
        enrollments=Enrollment.objects.filter(user_id=request.user.id).order_by('-start_date')
        serializer=EnrollmentSerializer(enrollments,many=True)
        return response.Response(data=serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'],detail=False,url_path='unpaid')
    def show_enrollments_not_paid(self,request):
        if not request.user.is_authenticated:
            return response.Response(data={'failed' : 'User Not Logged In'},status=status.HTTP_401_UNAUTHORIZED)
        update_enrollment_left_count()
        expire_enrollments()

        enrollments=Enrollment.objects.filter(user_id=request.user.id).order_by('-start_date')

        serializer=EnrollmentSerializer(enrollments,many=True)
        return response.Response(data=serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'],detail=False,url_path='current')
    def show_current(self,request):
        if not request.user.is_authenticated:
            return response.Response(data={'failed' : 'User Not Logged In'},status=status.HTTP_401_UNAUTHORIZED)
        help='Check courses that the customer had registered'
        update_enrollment_left_count()
        expire_enrollments()
        enrollments=Enrollment.objects.filter(user_id=request.user.id,valid=True,left_count__gt=0)
        serializer=EnrollmentSerializer(enrollments,many=True)
        return response.Response(data=serializer.data,status=status.HTTP_200_OK)

    @action(methods=['get'],detail=True,url_path='records')
    def show_records(self,request,pk):
        if not request.user.is_authenticated:
            return response.Response(data={'failed' : 'User Not Logged In'},status=status.HTTP_401_UNAUTHORIZED)
        enrollment=get_object_or_404(Enrollment,pk=pk)
        records=enrollment.records.all()
        serializer=RecordSerializer(records,many=True)

        return response.Response(data=serializer.data,status=status.HTTP_200_OK)

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class=AppointmentSerializer
    queryset=Appointment.objects.all()
    permissions_classes=[permissions.IsAuthenticated]

    serializer_classes = {
        'make_appointment' :AppointmentMakeSerializer
    }

    @action(methods=['post'],detail=False,url_path='make')
    def make_appointment(self,request):
        if not request.user.is_authenticated:
            return response.Response(data={'failed' : 'User Not Logged In'},status=status.HTTP_401_UNAUTHORIZED)

        appointment = Appointment.objects.create(user_id=request.user.id,
                                                date=request.data['date'],
                                                time=request.data['time'],
                                                level=request.data['level'],
                                                note=request.data['note'])
        serializer=AppointmentSerializer(appointment)
        return response.Response(data=serializer.data,status=status.HTTP_201_CREATED)

    @action(methods=['get'],detail=False,url_path='show')
    def show_appointments(self,request):
        if not request.user.is_authenticated:
            return response.Response(data={'failed' : 'User Not Logged In'},status=status.HTTP_401_UNAUTHORIZED)
        appointments=Appointment.objects.filter(user_id=request.user.id)
        serializer=AppointmentSerializer(appointments,many=True)
        return response.Response(data=serializer.data,status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class TeacherViewSet(viewsets.ModelViewSet):
    serializer_class=TeacherSerializer
    queryset=Teacher.objects.all()
