from django.test import TestCase
from django.test import SimpleTestCase
from django.urls import resolve, reverse

# -----------------------------------------------------------------------

from auth_prime.views import user_credential_API
from auth_prime.views import user_profile_API
from auth_prime.views import admin_credential_API
from auth_prime.views import admin_privilege_API

# -----------------------------------------------------------------------

class Test_Urls(SimpleTestCase):

    def test_user_credential_api_url_resolved(self):
        url = reverse("API_USER_CRED")
        self.assertEquals(resolve(url).func, user_credential_API)
    
    def test_user_profile_api_url_resolved(self):
        url = reverse("API_USER_PROF")
        self.assertEquals(resolve(url).func, user_profile_API)
    
    def test_user_profile_api_url_resolved(self):
        url = reverse("API_USER_PROF")
        self.assertEquals(resolve(url).func, user_profile_API)
    
    def test_admin_credential_api_url_resolved(self):
        url = reverse("API_ADMIN_CRED")
        self.assertEquals(resolve(url).func, admin_credential_API)
    
    def test_admin_privilege_api_url_resolved(self):
        url = reverse("API_ADMIN_PRIV")
        self.assertEquals(resolve(url).func, admin_privilege_API)

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------