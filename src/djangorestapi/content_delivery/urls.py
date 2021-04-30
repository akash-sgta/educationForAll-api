from django.conf.urls import url

from content_delivery import views

urlpatterns = [

    url(r'api/content/coordinator/(?P<job>\w*)/(?P<pk>\d*)', views.api_coordinator_view, name="Coordinator_View"),
    url(r'api/content/subject/(?P<job>\w*)/(?P<pk>\d*)', views.api_subject_view, name="Subject_View"),
    
    url(r'api/content/forum/(?P<job>\w*)/(?P<pk>\d*)', views.api_forum_view, name="Forum_View"),
    url(r'api/content/reply/(?P<job>\w*)/(?P<pk>\d*)', views.api_reply_view, name="Reply_View"),
    url(r'api/content/reply2reply/(?P<job>\w*)/(?P<pk>\d*)', views.api_reply2reply_view, name="Reply2_View"),
    
    url(r'api/content/lecture/(?P<job>\w*)/(?P<pk>\d*)', views.api_lecture_view, name="Lecture_View"),
    url(r'api/content/assignment/(?P<job>\w*)/(?P<pk>\d*)', views.api_assignment_view, name="Assignment_View"),
    url(r'api/content/markAssignment/(?P<job>\w*)/(?P<pk>\d*)/(?P<pkk>\d*)', views.mark_assignment_view, name="Mark_Assignment_View"),
    url(r'api/content/post/(?P<job>\w*)/(?P<pk>\d*)', views.api_post_view, name="Post_View"),

    url(r'api/content/votes/(?P<word>\w*)/(?P<pk>\d*)/(?P<control>[+-]?)', views.api_votes_view, name="Votes"),
    
]