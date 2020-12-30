from background_task import background
import datetime
from django.db.models import F
from .models import *


@background(schedule=24 * 6 * 60)
def update_enrollment_left_count(user_id):
    user = User.objects.get(pk=user_id)
    user.enrollments.all().filter(valid=True,
                                  lesson_day=datetime.datetime.today().weekday(),
                                  lesson_time__lte=datetime.datetime.now().hour).update(left_count=F('left_count') - 1)
