from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from djangorestapi import views

schema_view = get_schema_view(
    openapi.Info(
        title="JASS EDUCATION-BACKEND API",
        default_version="v1",
        description="For frontend developers",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="akashofficial1998@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # url(r'^docs/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # url(r'^docs/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # url(r'^docs/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r"^djadmin", admin.site.urls),
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
