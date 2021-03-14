from django.contrib import admin

from user_personal.models import Diary
from user_personal.models import Submission
from user_personal.models import Notification
from user_personal.models import User_Notification_Int
from user_personal.models import Enroll
# ------------------------------------------
# Register your models here.

admin.site.register(Diary)
admin.site.register(Submission)
admin.site.register(Notification)
admin.site.register(User_Notification_Int)
admin.site.register(Enroll)