import random

from django.test import SimpleTestCase
from django.urls import resolve, reverse

getRandom = lambda a=-1000, b=1000: random.randint(a, b)
# -----------------------------------------------------------------------

from auth_prime.view.admin_credential import Admin_Credential_View
from auth_prime.view.admin_privilege import Admin_Privilege_View
from auth_prime.view.api_web_view import API_Web_View
from auth_prime.view.user_credential import User_Credential_View
from auth_prime.view.user_profile import User_Profile_View
from auth_prime.view.user_profile_image import User_Profile_Image_View

# -----------------------------------------------------------------------


class Test_Urls(SimpleTestCase):
    def test_user_resolved(self):
        url = reverse("User_Cred_View", args=[getRandom()])
        self.assertEquals(resolve(url).func.view_class, User_Credential_View)

    def test_profile_resolved(self):
        url = reverse("User_Prof_View", args=[getRandom()])
        self.assertEquals(resolve(url).func.view_class, User_Profile_View)

    def test_profile_image_resolved(self):
        url = reverse("User_Prof_Image_View", args=[getRandom()])
        self.assertEquals(resolve(url).func.view_class, User_Profile_Image_View)

    def test_admin_resolved(self):
        url = reverse("Admin_Cred_View", args=[getRandom()])
        self.assertEquals(resolve(url).func.view_class, Admin_Credential_View)

    def test_privilege_resolved(self):
        url = reverse("Admin_Prev_View", args=[getRandom()])
        self.assertEquals(resolve(url).func.view_class, Admin_Privilege_View)

    def test_api_view_resolved(self):
        url = reverse("API_TOKEN", args=[getRandom()])
        self.assertEquals(resolve(url).func.view_class, API_Web_View)
