from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from user_personal.models import Diary
from user_personal.serializer import Diary_Serializer

# ------------------------------------------------------------


class Diary_View(APIView):  # TODO : Only user can access their specific diaries

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
            diary_serialized = Diary_Serializer(data=request.data)
            diary_serialized.initial_data["user_ref"] = int(isAuthorizedUSER[1])
            if diary_serialized.is_valid():
                diary_serialized.save()
                data["success"] = True
                data["data"] = diary_serialized.data
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data["success"] = False
                data["message"] = f"SERIALIZING_ERROR : {diary_serialized.errors}"
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if not isAuthorizedUSER[0]:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    if int(pk) == 0:  # TODO : Show all of user diaries
                        diary_ref = Diary.objects.filter(user_ref=isAuthorizedUSER[1])
                        diary_serialized = Diary_Serializer(diary_ref, many=True).data
                    else:  # TODO : Show specific of user diary
                        diary_ref = Diary.objects.get(user_ref=isAuthorizedUSER[1], pk=pk)
                        diary_serialized = Diary_Serializer(diary_ref, many=False).data
                except Diary.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_DIARY_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data["success"] = True
                    data["data"] = diary_serialized
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/personal/diary/<id>"}
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
            if not isAuthorizedUSER[0]:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    diary_ref = Diary.objects.get(user_credential_id=isAuthorizedUSER[1], diary_id=pk)
                except Diary.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_DIARY_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    diary_serialized = Diary_Serializer(diary_ref, data=request.data)
                    diary_serialized.initial_data["user_ref"] = isAuthorizedUSER[1]
                    if diary_serialized.is_valid():
                        diary_serialized.save()
                        data["success"] = True
                        data["data"] = diary_serialized.data
                        return Response(data=data, status=status.HTTP_201_CREATED)
                    else:
                        data["success"] = False
                        data["message"] = f"SERIALIZING_ERROR : {diary_serialized.errors}"
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/personal/diary/<id>"}
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
                    diary_ref = Diary.objects.get(user_ref=isAuthorizedUSER[1], pk=pk)
                except Diary.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_DIARY_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    diary_ref.delete()
                    data["success"] = True
                    data["message"] = "DIARY_DELETED"
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/personal/diary/<id>"}
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

        data["name"] = "Diary"

        temp["POST"] = {"post_ref": "Number [FK]", "body": "String : unl"}
        temp["GET"] = None
        temp["PUT"] = {"post_ref": "Number [FK]", "body": "String : unl"}
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
