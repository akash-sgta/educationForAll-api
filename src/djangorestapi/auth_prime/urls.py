from django.conf.urls import url
from django.urls import path
from auth_prime import views

urlpatterns = [
    
    url(r'api/user/user/$', views.user_credential_API, name="API_USER_CRED"),
    url(r'api/user/profile/$', views.user_profile_API, name="API_USER_PROF"),
    url(r'api/user/profile/image/$', views.image_API, name="API_IMAGE"),
    url(r'api/admin/admin/$', views.admin_credential_API, name="API_ADMIN_CRED"),
    url(r'api/admin/privilege/$', views.admin_privilege_API, name="API_ADMIN_PRIV"),

    url(r'web/api/(?P<word>\w*)/$', views.api_token_web, name="API_TOKEN"),
    url(r'web/api/$', views.api_token_web, name="API_TOKEN"),
    # url(r'web/user/admin/privilege/$', views.admin_privilege_VIEW),

]