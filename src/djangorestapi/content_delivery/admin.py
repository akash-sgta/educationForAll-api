from django.contrib import admin

from content_delivery.models import (
    Coordinator,
    Subject,
    Subject_Coordinator,
    Post,
    Reply,
    ReplyToReply,
)

# -----------------------------------------------------------
# Register your models here.
admin.site.register(Coordinator)
admin.site.register(Subject)
admin.site.register(Subject_Coordinator)

admin.site.register(Post)
admin.site.register(Reply)
admin.site.register(ReplyToReply)
