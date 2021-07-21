from django.conf.urls import include, url

from user_personal.view.diary import Diary_View
from user_personal.view.enroll import Enroll_View
from user_personal.view.notification import Notification_View
from user_personal.view.submission import Submission_View as subNormalView
from user_personal.view.submission_mcq import Submission_View as subMCQView


urlpatterns = [
    url(r"^diary/(?P<pk>\d*)", Diary_View.as_view(), name="Diary_View"),
    url(r"^submission_normal/(?P<pk>\d*)/(?P<pkk>\d*)", subNormalView.as_view(), name="Submission_View"),
    url(r"^submission_multi/(?P<pk>\d*)/(?P<pkk>\d*)", subMCQView.as_view(), name="Submission_MCQ_View"),
    url(r"^notification/(?P<pk>\d*)", Notification_View.as_view(), name="Notification_View"),
    url(r"^enroll/(?P<pk>\d*)", Enroll_View.as_view(), name="Enroll_View"),
]
