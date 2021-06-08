from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.static import serve
from rest_framework import permissions

from djangorestapi import views


urlpatterns = [
    url(r"^djadmin/", admin.site.urls),
    url(r"^api/auth/", include("auth_prime.urls")),
    url(r"^api/content/", include("content_delivery.urls")),
    url(r"^api/personal/", include("user_personal.urls")),
    url(r"^api/analytics/", include("analytics.urls")),
    url(r"^checkserver/", views.check_server_status, name="CHECK_SERVER_STATUS"),
]

if settings.DEBUG:
    urlpatterns.extend(
        [
            url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}, name="MEDIA_SERVE"),
            url(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}, name="STATIC_SERVE"),
        ]
    )

# urlpatterns += url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT})
# urlpatterns += url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT})
