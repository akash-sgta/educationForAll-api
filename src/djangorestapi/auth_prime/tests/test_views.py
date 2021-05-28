import json
import random

from auth_prime.models import Api_Token
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APITestCase

getRandom = lambda: random.randint(-1000, 1000)
# ------------------------------------------------------------


class User_TestCase(APITestCase):
    databases = {"app_db"}

    def setUp(self):
        self.user_cred_url = reverse("User_Cred_View", args=[getRandom()])

    def initial(self):
        api_ref = Api_Token(
            name="TEST", email="TEST@TEST.com", password="TESTTESTTESTTEST", hash="123654789987456321", endpoint=6
        )
        api_ref.save()
        return api_ref.hash

    def test_signup(self):
        api = self.initial()
        data = {
            "action": "signup",
            "data": {
                "first_name": "Test",
                "middle_name": "User",
                "last_name": "Case",
                "email": "TestUserCase@domain.com",
                "password": "password",
                "security_question": None,
                "security_answer": None,
            },
        }
        HEADERS = {
            "HTTP_Authorization": f"Token {api}",
            "HTTP_uauth": "Token qwertyytrewq",
        }
        response = self.client.post(self.user_cred_url, data=data, format="json", **HEADERS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
