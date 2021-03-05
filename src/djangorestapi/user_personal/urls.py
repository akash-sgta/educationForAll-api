from django.conf.urls import url
from user_personal import views

urlpatterns = [
    
    url(r'api/personal/diary/$', views.diary_API, name="DIARY_API"),
    url(r'api/personal/submission/$', views.submission_API, name="SUBMISSION_API"),

]