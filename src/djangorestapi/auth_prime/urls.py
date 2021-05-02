from django.conf.urls import url
from django.urls import path
from auth_prime import views

urlpatterns = [

    url(r'api/user/cred/(?P<pk>\d*)', views.ucView.as_view(), name="User_Cred_View"),
    url(r'api/user/prof/(?P<pk>\d*)', views.upView.as_view(), name="User_Prof_View"),
    url(r'api/user/image/(?P<pk>\d*)', views.upiView.as_view(), name="User_Prof_Image_View"),
    url(r'api/admin/cred/(?P<pk>\d*)', views.acView.as_view(), name="Admin_Cred_View"),
    url(r'api/admin/prev/(?P<pk>\d*)', views.apView.as_view(), name="Admin_Prev_View"),

    url(r'web/api/(?P<word>\w*)/', views.api_token_web, name="API_TOKEN"),
    url(r'web/api/', views.api_token_web, name="API_TOKEN"),

]