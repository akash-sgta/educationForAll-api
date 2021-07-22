from django.conf.urls import url
from django.urls import path


from auth_prime.view.admin_credential import Admin_Credential_View
from auth_prime.view.admin_privilege import Admin_Privilege_View
from auth_prime.view.user_credential import User_Credential_View
from auth_prime.view.user_profile import User_Profile_View
from auth_prime.view.user_profile_image import User_Profile_Image_View

urlpatterns = [
    url(r"^user/cred/(?P<pk>\d*)", User_Credential_View.as_view(), name="User_Cred_View"),
    url(r"^user/prof/(?P<pk>\d*)", User_Profile_View.as_view(), name="User_Prof_View"),
    url(r"^user/image/(?P<pk>\d*)", User_Profile_Image_View.as_view(), name="User_Prof_Image_View"),
    url(r"^admin/cred/(?P<pk>\d*)", Admin_Credential_View.as_view(), name="Admin_Cred_View"),
    url(r"^admin/prev/(?P<pk>\d*)", Admin_Privilege_View.as_view(), name="Admin_Prev_View"),
]
