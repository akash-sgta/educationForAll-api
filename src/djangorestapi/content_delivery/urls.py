from django.conf.urls import url

from content_delivery.view.assignment_mcq import Assignment_View as assMCQView
from content_delivery.view.assignment_mcq_mark import Assignment_Mark_View as marksMCQView
from content_delivery.view.assignment_normal import Assignment_View as assNormalView
from content_delivery.view.assignment_normal_mark import Assignment_Mark_View as marksNormalView
from content_delivery.view.coordinator import Coordinator_View
from content_delivery.view.forum import Forum_View
from content_delivery.view.lecture import Lecture_View
from content_delivery.view.post import Post_View
from content_delivery.view.reply_1 import Reply_View as reply1
from content_delivery.view.reply_2 import Reply_View as reply2
from content_delivery.view.subject import Subject_View
from content_delivery.view.votes import Votes_View

urlpatterns = [
    # url(r"video/(?P<pk>\d*)", views.vView.as_view(), name="Video_View"),
    url(r"^coordinator/(?P<pk>\d*)", Coordinator_View.as_view(), name="Coordinator_View"),
    url(r"^subject/(?P<pk>\d*)", Subject_View.as_view(), name="Subject_View"),
    url(r"^forum/(?P<pk>\d*)", Forum_View.as_view(), name="Forum_View"),
    url(r"^reply/(?P<pk>\d*)", reply1.as_view(), name="Reply_Simple_View"),
    url(r"^replyD/(?P<pk>\d*)", reply2.as_view(), name="Reply_Deep_View"),
    url(r"^lecture/(?P<pk>\d*)", Lecture_View.as_view(), name="Lecture_View"),
    url(r"^assignment/(?P<pk>\d*)", assNormalView.as_view(), name="Assignment_View"),
    url(r"^assignment_mark/(?P<pk_a>\d+)/(?P<pk_s>\d+)$", marksNormalView.as_view(), name="Assignment_Mark_View"),
    url(r"^multi/(?P<pk>\d*)", assMCQView.as_view(), name="MCQ_View"),
    url(r"^multi_mark/(?P<pk_a>\d+)/(?P<pk_s>\d+)$", marksMCQView.as_view(), name="MCQ_Mark_View"),
    url(r"^post/(?P<pk>\d*)", Post_View.as_view(), name="Post_View"),
    url(r"^votes/(?P<word>\w*)/(?P<pk>\d*)/(?P<case>\w*)$", Votes_View.as_view(), name="Votes_View"),
]
