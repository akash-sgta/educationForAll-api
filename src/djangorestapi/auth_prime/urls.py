from django.conf.urls import url
from auth_prime import views

urlpatterns = [
    
    url(r'api/user/$', views.user_API),
    url(r'api/user/([0-9]*)$', views.user_API),

    url(r'api/admin/$', views.admin_API),
    url(r'api/admin/([0-9]*)$', views.admin_API),

    url(r'api/admin/privilege/$', views.admin_privilege_API),
    url(r'api/admin/privilege/([0-9]*)$', views.admin_privilege_API),

    # url(r'api/token/$', views.token_API),
    # url(r'api/token/([0-9]*)$', views.token_API),

]