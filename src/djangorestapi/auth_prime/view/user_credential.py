import threading

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
    create_password_hashed,
    create_token,
)

from auth_prime.models import User, Profile, User_Token, Image
from auth_prime.serializer import User_Serializer

from cronjobs.bot import bot

# ------------------------------------------------------------


class Forgot_Password(threading.Thread):
    def __init__(self, user, case=False):
        super().__init__(user.name)
        self.case = case

    @property
    def case(self, data):
        return self.__case

    @case.setter
    def case(self, data):
        if data not in (True, False):
            self.__case = False
        else:
            self.__case = data

    def run(self):
        user = User_Serializer(self.user, many=False).data
        if user["telegram_id"] == None:
            return False
        else:
            try:
                new_password = create_token(12)
                text = "<b>Forgot Password Initiated</b>"
                text += f"\n by <i>{user['first_name']} {user['last_name']}</i>"
                text += "\n\nNew Password ==> "
                text += f"\n\n<b>{new_password}</b>"
                bot.send_notification(user["telegram_id"], text)
                self.user.password = create_password_hashed(new_password)
                self.user.save()
            except Exception as ex:
                print("[x] ForgotPass EX : ", ex)
                return False
            else:
                return True


class User_Credential_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        isAuthorizedUSER = am_I_Authorized(request, "USER")
        if (
            request.data["action"].lower() == "signin"
        ):  # TODO : If user is already signed in through cache [x]don't let signin again
            if isAuthorizedUSER[0]:
                data["success"] = False
                data["message"] = "USER_ALREADY_LOGGED_IN"
                return Response(data=data, status=status.HTTP_403_FORBIDDEN)
            else:
                myData = request.data["data"]
                try:
                    user_ref = User.objects.get(email=myData["email"].lower())
                except User.DoesNotExist:
                    data["success"] = False
                    data["message"] = "EMAIL_NOT_REGISTERED"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    hash = create_password_hashed(myData["password"])
                    old = user_ref.password
                    if user_ref.password != create_password_hashed(myData["password"]):
                        data["success"] = False
                        data["message"] = "PASSWORD_INCORRECT"
                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        data["success"] = True
                        data["data"] = {"JWT": create_token(user_ref)}
                        return Response(data=data, status=status.HTTP_201_CREATED)

        elif request.data["action"].lower() == "signup":
            if isAuthorizedUSER[0]:  # TODO : If user is already signed in through cache [x]don't let signin again
                data["success"] = False
                data["message"] = "USER_ALREADY_LOGGED_IN"
                return Response(data=data, status=status.HTTP_403_FORBIDDEN)
            else:
                user_de_serialized = User_Serializer(data=request.data["data"])
                user_de_serialized.initial_data["email"] = user_de_serialized.initial_data["email"].lower()
                try:
                    User.objects.get(email=user_de_serialized.initial_data["email"])
                except User.DoesNotExist:
                    user_de_serialized.initial_data["password"] = create_password_hashed(
                        user_de_serialized.initial_data["password"]
                    )
                    if user_de_serialized.is_valid():
                        user_de_serialized.save()
                        user_de_serialized.data
                        data["success"] = True
                        user_ref = User.objects.get(pk=user_de_serialized.data["id"])
                        data["data"] = {
                            "JWT": create_token(user_ref),
                            "data": user_de_serialized.data,
                        }
                        data["data"]["data"]["password"] = "■■REDACTED■■"
                        return Response(data=data, status=status.HTTP_201_CREATED)
                    else:
                        data["success"] = False
                        data["message"] = f"SERIALIZING_ERRORS : {user_de_serialized.errors}"
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data["success"] = False
                    data["message"] = "EMAIL_ALREADY_REGISTERED"
                    return Response(data=data, status=status.HTTP_403_FORBIDDEN)

        elif request.data["action"].lower() == "forgotp":
            try:
                myData = request.data["data"]
                user_ref = User.objects.get(email=myData["email"].lower())
            except User.DoesNotExist:
                data["success"] = False
                data["message"] = "EMAIL_NOT_REGISTERED"
                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
            else:
                forgot_password_thread = Forgot_Password(user_ref)
                data["success"] = True
                data["message"] = "CHECK_TELEGRAM"
                forgot_password_thread.start()
                return Response(data=data, status=status.HTTP_208_ALREADY_REPORTED)

    def get(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    if int(pk) == 0:  # TODO : User asking to read own credentials
                        user_ref = User.objects.get(pk=isAuthorizedUSER[1])
                        data["success"] = True
                        data["data"] = User_Serializer(user_ref, many=False).data

                        del data["data"]["password"]
                        del data["data"]["profile_ref"]
                        del data["data"]["telegram_id"]
                        del data["data"]["security_question"]
                        del data["data"]["security_answer"]
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif int(pk) == 87795962440396049328460600526719:  # TODO : ADMIN asking to read everyone's cred
                        isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                        if isAuthorizedADMIN > 0:
                            user_ref_all = User.objects.all()
                            data["success"] = True
                            data["data"] = User_Serializer(user_ref_all, many=True).data
                            for i in range(len(data["data"])):
                                del data["data"][i]["password"]
                                del data["data"][i]["profile_ref"]
                                del data["data"][i]["telegram_id"]
                                del data["data"][i]["security_question"]
                                del data["data"][i]["security_answer"]
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = "USER_NOT_ADMIN"
                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:  # TODO : ADMIN asking to read indivisual select user cred
                        isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                        if isAuthorizedADMIN > 0:
                            try:
                                user_ref = User.objects.get(pk=int(pk))
                            except User.DoesNotExist:
                                data["success"] = False
                                data["message"] = "USER_ID_INVALID"
                                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                data["success"] = True
                                data["data"] = User_Serializer(user_ref, many=False).data

                                del data["data"]["password"]
                                del data["data"]["profile_ref"]
                                del data["data"]["telegram_id"]
                                del data["data"]["security_question"]
                                del data["data"]["security_answer"]
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = "USER_NOT_ADMIN"
                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("USER_GET_EX : ", ex)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/user/cred/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):  # FIXME : Add admin access to change password of users
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if int(pk) == 0:  # TODO : User changing self data
                    user_ref = User.objects.get(pk=isAuthorizedUSER[1])
                    user_de_serialized = User_Serializer(user_ref, data=request.data)
                    user_de_serialized.initial_data["pk"] = isAuthorizedUSER[1]
                    user_de_serialized.initial_data["email"] = user_de_serialized.initial_data["email"].lower()
                    try:
                        email_check = User.objects.get(email=user_de_serialized.initial_data["email"])
                    except User.DoesNotExist:
                        flag = True
                    else:
                        if email_check.pk != isAuthorizedUSER[1]:
                            flag = False
                        else:
                            flag = True
                    finally:
                        if not flag:
                            data["success"] = False
                            data["message"] = "EMAIL_ALREADY_REGISTERED"
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            if user_de_serialized.is_valid():
                                user_de_serialized.save()
                                data["success"] = True
                                data["data"] = user_de_serialized.data
                                return Response(data=data, status=status.HTTP_201_CREATED)
                            else:
                                data["success"] = False
                                data["message"] = f"SERIALIZING_ERROR : {user_de_serialized.errors}"
                                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/user/cred/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    if int(pk) == 0:  # TODO : Self User cred delete
                        user_ref = User.objects.get(pk=isAuthorizedUSER[1])
                        if user_ref.profile_ref != None:
                            if user_ref.profile_ref.image_ref != None:
                                user_ref.profile_ref.image_ref.delete()
                            user_ref.profile_ref.delete()
                        user_ref.delete()
                        data["success"] = True
                        data["message"] = "USER_DELETED"
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif int(pk) == 87795962440396049328460600526719:  # TODO : User logout
                        try:
                            user_token_ref = User_Token.objects.get(user_ref=isAuthorizedUSER[1])
                        except User_Token.DoesNotExist:
                            data["success"] = True
                            data["message"] = "USER_ALREADY_LOGGED_OUT"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            user_token_ref.delete()
                            data["success"] = True
                            data["message"] = "USER_LOGGED_OUT"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif int(pk) == 13416989436929794359012690353783:  # TODO : ADMIN delete all user cred
                        if am_I_Authorized(request, "ADMIN") > 0:
                            User.objects.all().exclude(pk=isAuthorizedUSER[1]).delete()
                            user_ref = User.objects.get(pk=isAuthorizedUSER[1])
                            if user_ref.profile_ref != None:
                                if user_ref.profile_ref.image_ref != None:
                                    Image.objects.all().exclude(pk=user_ref.profile_ref.image_ref.pk).delete()
                                else:
                                    Image.objects.all().delete()
                                Profile.objects.all().exclude(pk=user_ref.profile_ref.pk).delete()
                            else:
                                Image.objects.all().delete()
                                Profile.objects.all().delete()
                            data["success"] = True
                            data["message"] = "ADMIN : All_USER_DELETED"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = "USER_NOT_ADMIN"
                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:  # TODO : Admin deletes selected user
                        if am_I_Authorized(request, "ADMIN") > 0:
                            try:
                                user_ref = User.objects.get(pk=pk)
                            except User.DoesNotExist:
                                data["success"] = False
                                data["message"] = "USER_ID_INVALID"
                                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                if user_ref.profile_ref != None:
                                    if user_ref.profile_ref.image_ref != None:
                                        user_ref.profile_ref.image_ref.delete()
                                    user_ref.profile_ref.delete()
                                user_ref.delete()
                                data["success"] = True
                                data["message"] = "ADMIN : USER_DELETED"
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = "USER_NOT ADMIN"
                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("USER_CRED_DELETE EX : ", ex)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/user/cred/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        temp = dict()

        data["Allow"] = "POST GET PUT DELETE OPTIONS".split()

        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()

        data["name"] = "User_Credential"

        temp["POST"] = (
            {
                "action": "signup",
                "data": {
                    "first_name": "String : 32",
                    "middle_name": "String : 32 / null",
                    "last_name": "String : 32",
                    "email": "String : 128",
                    "password": "String : 64",
                    "telegram_id": "String : 64",
                    "security_question": "String : 128",
                    "security_answer": "String : 128",
                    "profile_ref": "Number : FK",
                },
            },
            {"action": "signin", "data": {"email": "Email", "password": "String"}},
        )
        temp["GET"] = None
        temp["PUT"] = {
            "first_name": "String : 32",
            "middle_name": "String : 32 / null",
            "last_name": "String : 32",
            "email": "String : 128",
            "password": "String : 64",
            "telegram_id": "String : 64",
            "security_question": "String : 128",
            "security_answer": "String : 128",
            "profile_ref": "Number : FK",
        }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
