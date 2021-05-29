from django.conf.urls import url
from django.urls import path

# ---------------------------------------------------

from analytics import views

# ---------------------------------------------------

urlpatterns = [
    url(r"ticket/(?P<pk>\d*)", views.tView.as_view(), name="Ticket_View"),
    url(r"log/(?P<dd>[1-31]+)-(?P<mm>[1-12]+)-(?P<yyyy>[1960-9999]+)", views.lView.as_view(), name="Log_View"),
]
