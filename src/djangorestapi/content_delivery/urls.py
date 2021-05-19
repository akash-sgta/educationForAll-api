from django.conf.urls import url

from content_delivery import views

urlpatterns = [
    url(r"api/content/coordinator/(?P<pk>\d*)", views.cView.as_view(), name="Coordinator_View"),
    url(r"api/content/subject/(?P<pk>\d*)", views.sView.as_view(), name="Subject_View"),
    url(r"api/content/forum/(?P<pk>\d*)", views.fView.as_view(), name="Forum_View"),
    url(r"api/content/reply/(?P<pk>\d*)", views.r1View.as_view(), name="Reply_Simple_View"),
    url(r"api/content/replyD/(?P<pk>\d*)", views.r2View.as_view(), name="Reply_Deep_View"),
    url(r"api/content/lecture/(?P<pk>\d*)", views.lView.as_view(), name="Lecture_View"),
    url(r"api/content/assignment/(?P<pk>\d*)", views.a1View.as_view(), name="Assignment_View"),
    # url(r"api/content/video/(?P<pk>\d*)", views.vView.as_view(), name="Video_View"),
    url(r"api/content/mark/(?P<pk_a>\d+)/(?P<pk_s>\d+)$", views.a2View.as_view(), name="Mark_Assignment_View"),
    url(r"api/content/post/(?P<pk>\d*)", views.pView.as_view(), name="Post_View"),
    url(r"api/content/votes/(?P<word>\w*)/(?P<pk>\d*)/(?P<case>\w*)$", views.vView.as_view(), name="Votes_View"),
]
