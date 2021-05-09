from django.conf.urls import url
from django.urls import path

# ---------------------------------------------------

from analytics import views

# ---------------------------------------------------

urlpatterns = [
    
    url(r'api/analytics/ticket/(?P<pk>\d*)', views.tView.as_view(), name="Ticket_View"),
    url(r'api/analytics/log/(?P<date>[0-9-]*)', views.lView.as_view(), name="Log_View"),

]