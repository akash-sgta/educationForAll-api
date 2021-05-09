from django.conf.urls import url, include

from user_personal import views

urlpatterns = [
    
    url(r'api/personal/diary/(?P<pk>\d*)', views.dView.as_view(), name="Diary_View"),
    url(r'api/personal/submission/(?P<pk_1>\d*)-(?P<pk_2>\d*)', views.sView.as_view(), name="Submission_View"),
    url(r'api/personal/notification/(?P<pk>\d*)', views.nView.as_view(), name="Notification_View"),
    url(r'api/personal/enroll/(?P<pk>\d*)', views.eView.as_view(), name="Enroll_View"),

]