from django.conf.urls import url
from django.urls import path
from auth_prime import views

urlpatterns = [

    url(r'api/user/cred/(?P<job>\w*)/(?P<pk>\d*)', views.api_user_cred_view, name="User_Cred_View"),
    url(r'api/user/prof/(?P<job>\w*)/(?P<pk>\d*)', views.api_user_prof_view, name="User_Prof_View"),
    url(r'api/user/image/(?P<job>\w*)/(?P<pk>\d*)', views.api_user_prof_image_view, name="User_Prof_Image_View"),
    url(r'api/admin/cred/(?P<job>\w*)/(?P<pk>\d*)', views.api_admin_cred_view, name="Admin_Cred_View"),
    url(r'api/admin/prev/(?P<job>\w*)/(?P<pk>\d*)', views.api_admin_priv_view, name="Admin_Prev_View"),

    url(r'web/api/(?P<word>\w*)/', views.api_token_web, name="API_TOKEN"),
    url(r'web/api/', views.api_token_web, name="API_TOKEN"),

]