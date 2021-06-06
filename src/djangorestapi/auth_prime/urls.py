from django.conf.urls import url
from django.urls import path
from auth_prime import views

urlpatterns = [
    url(r"user/cred/(?P<pk>\d*)", views.ucView.as_view(), name="User_Cred_View"),
    url(r"user/prof/(?P<pk>\d*)", views.upView.as_view(), name="User_Prof_View"),
    url(r"user/image/(?P<pk>\d*)", views.upiView.as_view(), name="User_Prof_Image_View"),
    url(r"admin/cred/(?P<pk>\d*)", views.acView.as_view(), name="Admin_Cred_View"),
    url(r"admin/prev/(?P<pk>\d*)", views.apView.as_view(), name="Admin_Prev_View"),
    url(r"web/(?P<word>\w*)", views.apiView.as_view(), name="API_TOKEN"),
]
