from django.conf.urls import url
from django.urls import path

from analytics.view.log import Log_View
from analytics.view.permalink import Permalink_View
from analytics.view.ticket import Ticket_View

urlpatterns = [
    url(r"^ticket/(?P<pk>\d*)", Ticket_View.as_view(), name="Ticket_View"),
    url(r"^log/(?P<dd>[1-31]+)/(?P<mm>[1-12]+)/(?P<yyyy>[1960-9999]+)", Log_View.as_view(), name="Log_View"),
    url(r"^perm/(?P<word>[a-zA-Z0-9]+)", Permalink_View.as_view(), name="Perma_View"),
]
