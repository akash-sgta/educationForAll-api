from django.contrib import admin

from user_personal.models import Diary, Submission

# Register your models here.

admin.site.register(Diary)
admin.site.register(Submission)