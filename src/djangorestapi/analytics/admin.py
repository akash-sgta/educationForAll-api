from django.contrib import admin

from analytics.models import (
    Ticket,
    Log,
)

# -------------------------------------
# Register your models here.

admin.site.register(Ticket)
admin.site.register(Log)
