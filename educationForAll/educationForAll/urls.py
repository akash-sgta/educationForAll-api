from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve
from .views import check_server_status

## ================================================================================================= ##

urlpatterns = [
    url(r"^django-admin/", admin.site.urls),
    url(r"^checkserver/", check_server_status, name="CHECK_SERVER_STATUS"),
    # ---------------------------------------------------------
    # url(r"^api/auth/", include("auth_prime.urls")),
    # url(r"^api/content/", include("content_delivery.urls")),
    # url(r"^api/personal/", include("user_personal.urls")),
    # url(r"^api/analytics/", include("analytics.urls")),
    # url(r"^web/(?P<word>\w*)", API_Web_View.as_view(), name="API_TOKEN"),
]

if settings.DEBUG:
    urlpatterns.extend(
        [
            url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}, name="MEDIA_SERVE"),
            url(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}, name="STATIC_SERVE"),
        ]
    )
