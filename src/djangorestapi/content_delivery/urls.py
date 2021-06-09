from django.conf.urls import url

from content_delivery import views

urlpatterns = [
    # url(r"video/(?P<pk>\d*)", views.vView.as_view(), name="Video_View"),
    url(r"^coordinator/(?P<pk>\d*)", views.cView.as_view(), name="Coordinator_View"),
    url(r"^subject/(?P<pk>\d*)", views.sView.as_view(), name="Subject_View"),
    url(r"^forum/(?P<pk>\d*)", views.fView.as_view(), name="Forum_View"),
    url(r"^reply/(?P<pk>\d*)", views.r1View.as_view(), name="Reply_Simple_View"),
    url(r"^replyD/(?P<pk>\d*)", views.r2View.as_view(), name="Reply_Deep_View"),
    url(r"^lecture/(?P<pk>\d*)", views.lView.as_view(), name="Lecture_View"),
    url(r"^assignment/(?P<pk>\d*)", views.a11View.as_view(), name="Assignment_View"),
    url(r"^assignment_mark/(?P<pk_a>\d+)/(?P<pk_s>\d+)$", views.a12View.as_view(), name="Assignment_Mark_View"),
    url(r"^multi/(?P<pk>\d*)", views.a21View.as_view(), name="MCQ_View"),
    url(r"^multi_mark/(?P<pk_a>\d+)/(?P<pk_s>\d+)$", views.a22View.as_view(), name="MCQ_Mark_View"),
    url(r"^post/(?P<pk>\d*)", views.pView.as_view(), name="Post_View"),
    url(r"^votes/(?P<word>\w*)/(?P<pk>\d*)/(?P<case>\w*)$", views.vView.as_view(), name="Votes_View"),
]
