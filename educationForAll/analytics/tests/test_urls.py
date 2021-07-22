import random

from django.test import SimpleTestCase
from django.urls import resolve, reverse

getRandom = lambda a=-1000, b=1000: random.randint(a, b)
# -----------------------------------------------------------------------

from analytics.view.log import Log_View
from analytics.view.ticket import Ticket_View

# -----------------------------------------------------------------------


class Test_Urls(SimpleTestCase):
    def test_ticket_resolved(self):
        url = reverse("Ticket_View", args=[getRandom()])
        self.assertEquals(resolve(url).func.view_class, Ticket_View)

    def test_log_resolved(self):
        url = reverse("Log_View", args=[1, 1, 1])
        self.assertEquals(resolve(url).func.view_class, Log_View)
