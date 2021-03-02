from django.conf.urls import url

from content_delivery import views

urlpatterns = [

    url(r'api/content/coordinator/$', views.coordinator_API, name="COORDINATOR_API"),
    url(r'api/content/subject/$', views.subject_API, name="SUBJECT_API"),
    url(r'api/content/forum/$', views.forum_API, name="FORUM_API"),
    url(r'api/content/reply/$', views.reply_API, name="REPLY_API"),
    url(r'api/content/lecture/$', views.lecture_API, name="LECTURE_API"),
    url(r'api/content/assignment/$', views.assignment_API, name="ASSIGNMENT_API"),
    url(r'api/content/post/$', views.post_API, name="POST_API"),
    
]