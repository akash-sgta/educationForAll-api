from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from content_delivery.models import Coordinator, Reply, ReplyToReply
from content_delivery.serializer import Reply_Serializer

# ------------------------------------------------------------


class Reply_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None):  # TODO : Users can add replies
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
            reply_de_serialized = Reply_Serializer(data=request.data)
            reply_de_serialized.initial_data["user_ref"] = isAuthorizedUSER[1]
            if reply_de_serialized.is_valid():
                reply_de_serialized.save()
                data["success"] = True
                data["data"] = reply_de_serialized.data
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data["success"] = False
                data["message"] = reply_de_serialized.errors
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):  # TODO : Users can see all replies indivisually
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
                    reply_ref = Reply.objects.get(pk=int(pk))
                except Reply.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_RRPLY_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data["success"] = True
                    data["data"] = {
                        "reply": Reply_Serializer(reply_ref, many=False).data,
                        "reply2": [
                            one["pk"] for one in ReplyToReply.objects.filter(reply_ref=reply_ref).order_by("-pk").values("pk")
                        ],
                    }
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/content/reply/<simple_reply_id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):  # TODO : Users can edit own replies
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
                    reply_ref = Reply.objects.get(pk=int(pk), user_ref=isAuthorizedUSER[1])
                except Reply.DoesNotExist:
                    data["success"] = False
                    data["message"] = "REPLY_DOES_NOT_EXIST"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    reply_de_serialized = Reply_Serializer(reply_ref, data=request.data)
                    if reply_de_serialized.is_valid():
                        reply_de_serialized.save()
                        data["success"] = True
                        data["data"] = reply_de_serialized.data
                        return Response(data=data, status=status.HTTP_201_CREATED)
                    else:
                        data["success"] = False
                        data["message"] = reply_de_serialized.errors
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/content/reply/<simple_reply_id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):  # TODO : Users can delete own replies
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
                    reply_ref = Reply.objects.get(pk=int(pk), user_ref=isAuthorizedUSER[1])
                except Reply.DoesNotExist:
                    data["success"] = False
                    data["message"] = "REPLY_DOES_NOT_EXIST"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    reply_ref.delete()
                    data["success"] = True
                    data["message"] = "REPLY_DELETED"
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/content/reply/<simple_reply_id>"}
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

        data["name"] = "Reply_Main"

        temp["POST"] = {"forum_ref": "Number [FK]", "body": "String : unl"}
        temp["GET"] = None
        temp["PUT"] = {"forum_ref": "Number [FK]", "body": "String : unl"}
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
