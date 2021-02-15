from django.conf.urls import url
from auth_prime import views

urlpatterns = [
    
    url(r'api/user/user/$', views.user_credential_API),
    url(r'api/user/profile/$', views.user_profile_API),
    url(r'api/admin/admin/$', views.admin_API),
    url(r'api/admin/privilege/$', views.admin_privilege_API),

    url(r'web/user/admin/$', views.admin_VIEW),
    url(r'web/user/admin/privilege/$', views.admin_privilege_VIEW),

]