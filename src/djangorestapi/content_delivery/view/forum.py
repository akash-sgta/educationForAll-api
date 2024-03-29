from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from content_delivery.models import Coordinator, Forum, Reply
from content_delivery.serializer import Forum_Serializer

# ------------------------------------------------------------


class Forum_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None):  # TODO : Only Coordinators can create
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
            try:
                coordinator_ref = Coordinator.objects.get(user_ref=isAuthorizedUSER[1])
            except Coordinator.DoesNotExist:
                data["success"] = False
                data["message"] = "USER_NOT_COORDINATOR"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                forum_de_serialized = Forum_Serializer(data=request.data)
                if forum_de_serialized.is_valid():
                    forum_de_serialized.save()
                    data["success"] = True
                    data["data"] = forum_de_serialized.data
                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    data["success"] = False
                    data["message"] = forum_de_serialized.errors
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):  # TODO : See all access granted to no one--# FIX : See if changes needed
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
                    forum_ref = Forum.objects.get(pk=pk)
                except Forum.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_FORUM_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data["success"] = True
                    data["data"] = {
                        "forum": Forum_Serializer(forum_ref, many=False).data,
                        "reply": [one["pk"] for one in Reply.objects.filter(forum_ref=int(pk)).order_by("-pk").values("pk")],
                    }
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/content/forum/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):  # TODO : Only Coordinators can delete--# FIX : All delete given to no one
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
                    coordinator_ref = Coordinator.objects.get(user_ref=isAuthorizedUSER[1])
                except Coordinator.DoesNotExist:
                    data["success"] = False
                    data["message"] = "USER_NOT_COORDINATOR"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        forum_ref = Forum.objects.get(pk=int(pk))
                    except Forum.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_FORUM_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        forum_ref.delete()
                        data["success"] = True
                        data["message"] = "FORUM_DELETED"
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/content/forum/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        temp = dict()

        data["Allow"] = "POST GET DELETE OPTIONS".split()

        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()

        data["name"] = "Forum"

        temp["POST"] = {}
        temp["GET"] = None
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
