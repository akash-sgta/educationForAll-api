from django.conf.urls import url
from django.urls import path

# ---------------------------------------------------

from analytics import views

# ---------------------------------------------------

urlpatterns = [
    
    url(r'api/analytics/ticket/(?P<job>\w*)/(?P<pk>\d*)', views.api_ticket_view, name="Ticket_View"),
    url(r'api/analytics/log/(?P<job>\w*)/(?P<date>[0-9-]*)', views.api_log_view, name="Log_View"),

]