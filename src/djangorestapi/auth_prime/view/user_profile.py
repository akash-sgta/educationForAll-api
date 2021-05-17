from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from auth_prime.models import User, Profile, Image
from auth_prime.serializer import Profile_Serializer

# ------------------------------------------------------------


class User_Profile_View(APIView):

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
        if isAuthorizedUSER[0] == False:
            data["success"] = False
            data["message"] = f"USER_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_ref = User.objects.get(pk=isAuthorizedUSER[1])
            if user_ref.user_profile_id in (None, ""):
                profile_de_serialized = Profile_Serializer(data=request.data)
                if profile_de_serialized.initial_data["prime"] == True and profile_de_serialized.initial_data[
                    "roll_number"
                ] in (
                    None,
                    "",
                ):
                    data["success"] = False
                    data["message"] = "STUDENT_REQUIRES_12_DIGIT_ROLL"
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if profile_de_serialized.is_valid():
                        profile_de_serialized.save()

                        profile_ref = Profile.objects.get(pk=profile_de_serialized.data["user_profile_id"])
                        user_ref.profile_ref = profile_ref
                        user_ref.save()

                        data["success"] = True
                        data["data"] = profile_de_serialized.data
                        return Response(data=data, status=status.HTTP_201_CREATED)
                    else:
                        data["success"] = False
                        data["message"] = f"SERIALIZING_ERROR : {profile_de_serialized.errors}"
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data["success"] = True
                data["message"] = "PROFILE_ALREADY_EXISTS"
                data["data"] = Profile_Serializer(user_ref.profile_ref, many=False).data
                return Response(data=data, status=status.HTTP_201_CREATED)

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
                    if int(pk) == 0:  # TODO : User reads self profile
                        user_ref = User.objects.get(pk=isAuthorizedUSER[1])
                        if user_ref.profile_ref in (None, ""):
                            data["success"] = False
                            data["message"] = "USER_PROFILE_DOES_NOT_EXIST"
                            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            data["success"] = True
                            data["data"] = Profile_Serializer(user_ref.profile_ref, many=False).data
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif int(pk) == 87795962440396049328460600526719:  # TODO : Admin reads all profile
                        if am_I_Authorized(request, "ADMIN") > 0:
                            data["success"] = True
                            data["data"] = Profile_Serializer(Profile.objects.all(), many=True).data
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = "USER_NOT_ADMIN"
                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:  # TODO : Admin reads selected user profile
                        try:
                            user_ref = User.objects.get(pk=pk)
                        except User.DoesNotExist:
                            data["success"] = False
                            data["message"] = "USER_ID_INVALID"
                            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            if user_ref.profile_ref == None:
                                data["success"] = False
                                data["message"] = "USER_PROFILE_DOES_NOT_EXIST"
                                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                data["success"] = True
                                data["data"] = Profile_Serializer(user_ref.profile_ref, many=False).data
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)

                except Exception as ex:
                    print("USER_PROF_GET EX : ", ex)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/user/prof/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
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
                user_ref = User.objects.get(pk=isAuthorizedUSER[1])
                if user_ref.profile_ref == None:
                    data["success"] = False
                    data["message"] = f"USER_HAS_NO_PROFILE"
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    profile_de_serialized = Profile_Serializer(user_ref.profile_ref, data=request.data)
                    if profile_de_serialized.initial_data["prime"] == True and profile_de_serialized.initial_data[
                        "user_roll_number"
                    ] in (
                        None,
                        "",
                    ):
                        data["success"] = False
                        data["message"] = "STUDENT_REQUIRES_12_DIGIT_ROLL"
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if profile_de_serialized.is_valid():
                            profile_de_serialized.save()
                            data["success"] = True
                            data["data"] = profile_de_serialized.data
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = f"SERIALIZING_ERROR : {profile_de_serialized.errors}"
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/user/prof/<id>"}
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
                    if int(pk) == 0:  # TODO : User deleting self profile
                        user_ref = User.objects.get(pk=isAuthorizedUSER[1])
                        if user_ref.profile_ref == None:
                            data["success"] = True
                            data["message"] = "USER_PROFILE_DOES_NOT_EXIST"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            if user_ref.profile_ref.image_ref != None:
                                user_ref.profile_ref.image_ref.delete()
                            user_ref.profile_ref.delete()
                            data["success"] = True
                            data["message"] = "USER_PROFILE_DELETED"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif int(pk) == 87795962440396049328460600526719:  # TODO : Admin deleting all user profiles
                        if am_I_Authorized(request, "ADMIN") > 0:
                            Profile.objects.all().delete()
                            Image.objects.all().delete()
                            data["success"] = True
                            data["message"] = "ADMIN : ALL_USER_PROFILES_DELETED"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = "USER_NOT_ADMIN"
                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:  # TODO : Admin deletes specific profile
                        if am_I_Authorized(request, "ADMIN") > 0:
                            try:
                                user_ref = User.objects.get(pk=pk)
                            except User.DoesNotExist:
                                data["success"] = False
                                data["message"] = "ADMIN : USER_ID_INVALID"
                                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                if user_ref.profile_ref == None:
                                    data["success"] = True
                                    data["message"] = "ADMIN : USER_PROFILE_DOES_NOT_EXIST"
                                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
                                else:
                                    if user_ref.profile_ref.image_ref != None:
                                        user_ref.profile_ref.image_ref.delete()
                                    user_ref.profile_ref.delete()
                                    data["success"] = True
                                    data["message"] = "ADMIN : USER_PROFILE_DELETED"
                                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = "USER_NOT_ADMIN"
                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/user/prof/<id>"}
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

        data["name"] = "User_Profile"

        temp["POST"] = {
            "headline": "String : 128",
            "bio": "String : unl",
            "english_efficiency": "Number : 1",
            "git_profile": "String : 256",
            "likedin_profile": "String : 256",
            "roll_number": "Number : 12",
            "prime": "Bool",
            "image_ref": "Number / null",
        }
        temp["GET"] = None
        temp["PUT"] = {
            "headline": "String : 128",
            "bio": "String : unl",
            "english_efficiency": "Number : 1",
            "git_profile": "String : 256",
            "likedin_profile": "String : 256",
            "roll_number": "Number : 12",
            "prime": "Bool",
            "image_ref": "Number / null",
        }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
