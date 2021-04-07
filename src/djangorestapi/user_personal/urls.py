from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from user_personal import views

# router = DefaultRouter()
# router.register('personal', views.DiaryViewSet)

urlpatterns = [
    
    url(r'api/personal/diary/(?P<job>\w*)/(?P<pk>\d*)', views.api_diary_view, name="Diary_View"),
    url(r'api/personal/submission/(?P<job>\w*)/(?P<pk>\d*)/(?P<pkk>\d*)', views.api_submission_view, name="Submission_View"),
    # url(r'api/personal/notification/(?P<job>\w+)/(?P<pk>\d*)', views.api_notification_view, name="Notification_View"),
    url(r'api/personal/enroll/(?P<job>\w*)/(?P<pk>\d*)', views.api_enroll_view, name="Enroll_View"),

]