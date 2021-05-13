from django.contrib import admin

from user_personal.models import (
    Diary,
    Submission,
    Notification,
    User_Notification_Int,
    Enroll,
    Assignment_Submission_Int
)

# ------------------------------------------
# Register your models here.

admin.site.register(Diary)
admin.site.register(Submission)
admin.site.register(Notification)
admin.site.register(User_Notification_Int)
admin.site.register(Enroll)
admin.site.register(Assignment_Submission_Int)