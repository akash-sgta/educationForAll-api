from django.contrib import admin

from analytics.models import Log, Permalink, Ticket

# -------------------------------------
# Register your models here.

admin.site.register(Ticket)
admin.site.register(Log)
admin.site.register(Permalink)
