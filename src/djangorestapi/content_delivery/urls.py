from django.conf.urls import url

from content_delivery import views

urlpatterns = [

    url(r'api/content/coordinator/$', views.coordinator_API),
    url(r'api/content/subject/$', views.subject_API),
    url(r'api/content/forum/$', views.forum_API),
    url(r'api/content/reply/$', views.reply_API),
    url(r'api/content/lecture/$', views.lecture_API),
    
]