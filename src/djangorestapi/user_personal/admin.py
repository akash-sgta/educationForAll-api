from django.contrib import admin

from user_personal.models import (
    Diary,
    Submission,
    Notification,
    User_Notification,
    Enroll,
)

# ------------------------------------------
# Register your models here.

admin.site.register(Diary)
admin.site.register(Submission)
admin.site.register(Notification)
admin.site.register(User_Notification)
admin.site.register(Enroll)
