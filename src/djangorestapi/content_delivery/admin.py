from django.contrib import admin

from content_delivery.models import Coordinator
from content_delivery.models import Subject
from content_delivery.models import Subject_Coordinator_Int
from content_delivery.models import Video
from content_delivery.models import Forum
from content_delivery.models import Reply
from content_delivery.models import Lecture
from content_delivery.models import Assignment
from content_delivery.models import Post
# -----------------------------------------------------------
# Register your models here.
admin.site.register(Coordinator)
admin.site.register(Subject)
admin.site.register(Video)
admin.site.register(Forum)
admin.site.register(Reply)
admin.site.register(Lecture)
admin.site.register(Assignment)
admin.site.register(Post)
admin.site.register(Subject_Coordinator_Int)