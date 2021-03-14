from django.contrib import admin

from analytics.models import Ticket
from analytics.models import Log
# -------------------------------------
# Register your models here.
admin.site.register(Ticket)
admin.site.register(Log)
