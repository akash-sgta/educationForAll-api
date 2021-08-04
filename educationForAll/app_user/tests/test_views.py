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
        self.user_cred_url = reverse("User_Cred_View", args=[0])
        api_ref = Api_Token(
            name="TEST", email="TEST@TEST.com", password="TESTTESTTESTTEST", hash="123654789987456321", endpoint=6
        )
        api_ref.save()
        self.api_key = api_ref.hash
        self.uauth = None

    def test_signup(self):
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
            "HTTP_Authorization": f"Token {self.api_key}",
            "HTTP_uauth": f"Token {self.uauth}",
        }
        response = self.client.post(self.user_cred_url, data=data, format="json", **HEADERS)

        # signup successful normal
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"RESP : {json.loads(response.content)}")  # signup

    def test_signin(self):
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
            "HTTP_Authorization": f"Token {self.api_key}",
            "HTTP_uauth": f"Token {self.uauth}",
        }
        response = self.client.post(self.user_cred_url, data=data, format="json", **HEADERS)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"RESP : {json.loads(response.content)}")  # signup
        self.uauth = json.loads(response.content)["data"]["JWT"]

        data = {
            "action": "signin",
            "data": {
                "email": "TestUserCase@domain.com",
                "password": "password",
            },
        }

        HEADERS = {
            "HTTP_Authorization": f"Token {self.api_key}",
            "HTTP_uauth": f"Token {None}",
        }
        response = self.client.post(self.user_cred_url, data=data, format="json", **HEADERS)
        # signin successful normal
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"RESP : {json.loads(response.content)}")
        # check if abiding with stored JWT
        self.assertEqual(json.loads(response.content)["data"]["JWT"], self.uauth, "DIFFERENCE IN JWT")

        HEADERS = {
            "HTTP_Authorization": f"Token {self.api_key}",
            "HTTP_uauth": f"Token {self.uauth}",
        }
        response = self.client.post(self.user_cred_url, data=data, format="json", **HEADERS)
        # signin unsuccessful as correct uauth exists
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, f"RESP : {json.loads(response.content)}")

    def test_signout(self):
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
            "HTTP_Authorization": f"Token {self.api_key}",
            "HTTP_uauth": f"Token {self.uauth}",
        }
        response = self.client.post(self.user_cred_url, data=data, format="json", **HEADERS)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"RESP : {json.loads(response.content)}")  # signup
        self.uauth = json.loads(response.content)["data"]["JWT"]

        HEADERS = {
            "HTTP_Authorization": f"Token {self.api_key}",
            "HTTP_uauth": f"Token {self.uauth}",
        }
        response = self.client.delete(self.user_cred_url[:-1] + "87795962440396049328460600526719", **HEADERS)

        # signout normal
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED, f"RESP : {json.loads(response.content)}")

    def test_user_delete(self):
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
            "HTTP_Authorization": f"Token {self.api_key}",
            "HTTP_uauth": f"Token {self.uauth}",
        }
        response = self.client.post(self.user_cred_url, data=data, format="json", **HEADERS)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"RESP : {json.loads(response.content)}")  # signup
        self.uauth = json.loads(response.content)["data"]["JWT"]

        HEADERS = {
            "HTTP_Authorization": f"Token {self.api_key}",
            "HTTP_uauth": f"Token {self.uauth}",
        }
        response = self.client.delete(self.user_cred_url[:-1] + "0", **HEADERS)

        # signout normal
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED, f"RESP : {json.loads(response.content)}")
