from django.conf.urls import url, include

from user_personal import views

urlpatterns = [
    url(r"diary/(?P<pk>\d*)", views.dView.as_view(), name="Diary_View"),
    url(r"submission/(?P<pk>\d*)/(?P<pkk>\d*)", views.sView.as_view(), name="Submission_View"),
    url(r"notification/(?P<pk>\d*)", views.nView.as_view(), name="Notification_View"),
    url(r"enroll/(?P<pk>\d*)", views.eView.as_view(), name="Enroll_View"),
]
