from django.conf.urls import url
from django.urls import path

from analytics import views

urlpatterns = [
    
    url(r'api/user/ticket/', views.ticket.run, name="API_TICKET"),
    url(r'api/log/', views.log.run, name="API_LOG"),

]