from django.conf.urls import url

from content_delivery import views

urlpatterns = [

    url(r'api/content/coordinator/', views.coordinator.run, name="COORDINATOR_API"),
    url(r'api/content/subject/', views.subject.run, name="SUBJECT_API"),
    url(r'api/content/forum/', views.forum.run, name="FORUM_API"),
    url(r'api/content/reply/', views.reply.run, name="REPLY_API"),
    url(r'api/content/lecture/', views.lecture.run, name="LECTURE_API"),
    url(r'api/content/assignment/', views.assignment.run, name="ASSIGNMENT_API"),
    url(r'api/content/post/', views.post.run, name="POST_API"),
    
]