from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from user_personal import views

# router = DefaultRouter()
# router.register('personal', views.DiaryViewSet)

urlpatterns = [
    
    url(r'api/personal/diary/(?P<job>\w+)/(?P<pk>\d*)', views.api_diary_view, name="Diary_View"),

    #url(r'api/personal/diary/', views.diary.run, name="DIARY_API"),
    url(r'api/personal/submission/', views.submission.run, name="SUBMISSION_API"),
    url(r'api/personal/notification/', views.notification.run, name="NOTIFICATION_API"),
    url(r'api/personal/enroll/', views.enroll.run, name="ENROLL_API"),

]