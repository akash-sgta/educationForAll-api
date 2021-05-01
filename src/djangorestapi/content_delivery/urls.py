from django.conf.urls import url

from content_delivery import views

urlpatterns = [

    url(r'api/content/coordinator/(?P<pk>\d*)', views.cView.as_view(), name="Coordinator_View"),
    url(r'api/content/subject/(?P<pk>\d*)', views.sView.as_view(), name="Subject_View"),
    url(r'api/content/forum/(?P<pk>\d*)', views.fView.as_view(), name="Forum_View"),
    url(r'api/content/reply/(?P<job>\w*)/(?P<pk>\d*)', views.api_reply_view, name="Reply_View"),
    url(r'api/content/lecture/(?P<job>\w*)/(?P<pk>\d*)', views.api_lecture_view, name="Lecture_View"),
    url(r'api/content/assignment/(?P<job>\w*)/(?P<pk>\d*)', views.api_assignment_view, name="Assignment_View"),
    url(r'api/content/post/(?P<job>\w*)/(?P<pk>\d*)', views.api_post_view, name="Post_View"),
    
]