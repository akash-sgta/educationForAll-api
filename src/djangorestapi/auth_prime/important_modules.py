from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from auth_prime.models import (
    Api_Token,
    User_Token,
    User,
    Admin,
    Privilege,
    Admin_Privilege,
)

from analytics.models import Log

from hashlib import sha256
import string
import random
import json
import threading

# --------------------------------------------------------


class Cookie(object):
    def __init__(self, hash=None):
        super().__init__()
        self._token = hash

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, data):
        self._token = data

    # ------------------------------------------
    # Cookie Push handle
    def setCookie(self, request, file_path=None, data=None, **kwargs):

        key_list = list(kwargs.keys())
        try:
            if (file_path == None) or (data == None):
                raise Exception("Required Arguments not found.")
            else:
                request.session.set_expiry(0)
                response = render(request, file_path, data)
                for item in key_list:
                    if item not in ("file_path", "data"):
                        response.set_cookie(f"{item}", kwargs[item])

        except Exception as ex:
            print(f"[x] SET COOKIE Ex : {str(ex)}")
            return redirect("API_TOKEN", word="signin")
        else:
            return response

    # ------------------------------------------
    # Cookie Pull handle
    def getCookie(self, request, *args):

        try:
            cookies = list()
            for arg in args:
                temp = request.COOKIES[str(arg)]
                cookies.append(temp)
            return cookies
        except Exception as ex:
            print(f"[x] GET COOKIE Ex : {str(ex)}")
            cookies.append(None)
            return cookies

    # ------------------------------------------
    def make_hash(self, *args):

        try:
            data = "&".join([str(arg) for arg in args])
            hashd = str(sha256(data.encode("utf-8")).digest())
        except Exception as ex:
            print(f"[x] HASH Ex : {str(ex)}")
            return None
        else:
            return hashd

    # ------------------------------------------
    def set_authentication_info(self, request=None, file_path=None, data=None, pk=None):

        try:
            if (file_path == None) or (data == None) or (pk == None):
                raise Exception("Necessary arguments not passed.")
            else:
                user = Api_Token.objects.get(pk=pk)
                tauth = f"{user.pk}::{self.make_hash(user.email, user.password)}"
        except Exception as ex:
            print(f"[x] SET AUTH Ex : {str(ex)}")
            return redirect("API_TOKEN", word="")
        else:
            return self.setCookie(request, file_path=file_path, data=data, tauth=tauth)

    # ------------------------------------------
    def revoke_authentication_info(self, request, file_path, data):

        try:
            if (file_path == None) or (data == None):
                raise Exception("Necessary arguments not passed.")
            else:
                response = render(request, file_path, data)
                response.delete_cookie("tauth")
        except Exception as ex:
            from django.shortcuts import redirect

            print(f"[x] REVOKE AUTH  Ex : {str(ex)}")
            return redirect("forum_home")
        else:
            return response

    # ------------------------------------------
    def check_authentication_info(self, request):
        try:
            user_credential = self.getCookie(request, "tauth")
            # if auth false or not initialized
            if user_credential[0] in (None, False, ""):
                return False, 1
            else:
                cookie_user = user_credential[0].split("::")
                try:
                    user = Api_Token.objects.get(pk=int(cookie_user[0]))
                except Api_Token.DoesNotExist:
                    return False, 2
                else:
                    if cookie_user[1] == self.make_hash(user.email, user.password):
                        return True, user.pk
                    else:
                        return False, 3
        except Exception as ex:
            print(f"[x] CHECK AUTH Ex : {str(ex)}")
            return False, 4


# --------------------------------------------------------


def am_I_Authorized(request, key):

    if key.lower() == "api":
        try:
            headers = request.headers
            if "Authorization" in headers:
                try:
                    api_token_ref = Api_Token.objects.get(hash=headers["Authorization"].split()[1])
                except Api_Token.DoesNotExist:
                    return (False, "API_KEY_UNAUTHORIZED")
                except IndexError:
                    return (False, "API_KEY_UNAUTHORIZED")
                else:
                    return (True, api_token_ref.pk)
            else:
                return (False, "HTTP_Header_Mismatch - Authorization")
        except Exception as ex:
            print("EX : ", ex)
            return (False, "HTTP_Header_Mismatch - Authorization")

    elif key.lower() == "user":
        try:
            headers = request.headers
            if "uauth" in headers:
                try:
                    user_token_ref = User_Token.objects.get(hash=headers["uauth"].split()[1])
                except User_Token.DoesNotExist:
                    return (False, "USER_HASH_UNAUTHORIZED")
                except IndexError:
                    return (False, "USER_HASH_UNAUTHORIZED")
                else:
                    return (True, user_token_ref.user_ref.pk)
            else:
                return (False, "HTTP_Header_Mismatch - uauth")
        except Exception as ex:
            print("EX : ", ex)
            return (False, "HTTP_Header_Mismatch - uauth")

    elif key.lower() == "admin":  # todo
        try:
            headers = request.headers
            if "uauth" in headers:
                try:
                    user_token_ref = User_Token.objects.get(hash=headers["uauth"].split()[1])
                except User_Token.DoesNotExist:
                    return 0
                except IndexError:
                    return 0
                else:
                    try:
                        admin_ref = Admin.objects.get(user_ref=user_token_ref.user_ref.pk)
                    except Admin.DoesNotExist:
                        return 0
                    else:
                        if admin_ref.prime == False:
                            return 2
                        else:
                            return 69  # TODO : ADMIN PRIME returns 69
            else:
                return 0

        except Exception as ex:
            print("EX : ", ex)
            return 0


def do_I_Have_Privilege(request, key):

    try:
        headers = request.headers
        if "uauth" in headers:
            try:
                user_token_ref = User_Token.objects.get(hash=headers["uauth"].split()[1])
            except User_Token.DoesNotExist:
                return False
            else:
                try:
                    admin_ref = Admin.objects.get(user_ref=user_token_ref.user_ref.pk)
                except Admin.DoesNotExist:
                    return False
                else:
                    try:
                        privilege_ref = Privilege.objects.get(name=key.upper())
                    except Privilege.DoesNotExist:
                        return False
                    else:
                        try:
                            Admin_Privilege.objects.get(
                                admin_ref=admin_ref,
                                privilege_ref=privilege_ref,
                            )
                        except Admin_Privilege.DoesNotExist:
                            return False
                        else:
                            return True
        else:
            return False
    except Exception as ex:
        print("EX : ", ex)
        return False


# --------------------------------------------------------


def create_password_hashed(password):
    sha256_ref = sha256()
    sha256_ref.update(f"ooga{password}booga".encode("utf-8"))
    return str(sha256_ref.digest())[:64].strip()


def random_generator(length=64):
    password_characters = string.ascii_letters + string.digits
    password = [random.choice(password_characters) for i in range(length)]
    return "".join(password)


def create_token(user_ref):
    try:
        user_token_ref = User_Token.objects.get(user_ref=user_ref.pk)
    except User_Token.DoesNotExist:
        user_token_ref = User_Token(user_ref=user_ref, hash=random_generator())
        user_token_ref.save()
    else:
        pass
    finally:
        return user_token_ref.hash


# --------------------------------------------------------


class Logger(threading.Thread):
    def __init__(self, api_id=None, method=None, action=None):
        super().__init__(name=f"{api_id}_{random_generator(8)}")
        self.api_id = api_id
        self.method = method.upper()
        self.action = action.upper()
        self.body = None

    def run(self, message=None):
        if message == None or method == None:
            pass
        else:
            self.body = message
            self.body["method"] = self.method
            log_ref_new = Log(api_ref=Api_Token.objects.get(pk=self.api_id), body=json.dumps(self.body, indent=4))
            log_ref_new.save()
