from django.conf.urls import url
from user_personal import views

urlpatterns = [
    
    url(r'api/diary/$', views.diary_API),
    url(r'api/diary/([0-9]*)$', views.diary_API),

    url(r'api/submission/$', views.submission_API),
    url(r'api/submission/([0-9]*)$', views.submission_API),

]