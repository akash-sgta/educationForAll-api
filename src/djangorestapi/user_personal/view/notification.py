from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from user_personal.models import Notification, User_Notification
from user_personal.serializer import Notification_Serializer

# ------------------------------------------------------------


class Notification_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

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
                if int(pk) == 0:  # TODO : User needs all notifications that have not been sent to TG
                    notifications = [
                        one.notification_ref
                        for one in User_Notification.objects.filter(pk=isAuthorizedUSER[1], prime_1=False).order_by(
                            "-notification_ref"
                        )
                    ]
                    data["success"] = True
                    data["data"] = Notification_Serializer(notifications, many=True).data
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:  # TODO : User needs specific notification
                    try:
                        notification_ref = Notification.objects.get(pk=int(pk))
                    except Notification.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_NOTIFICATION_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data["success"] = True
                        data["data"] = Notification_Serializer(notification_ref, many=False).data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/personal/notification/<id>"}
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
                    notification_ref = User_Notification.objects.get(user_ref=isAuthorizedUSER[1], pk=int(pk))
                except User_Notification.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_NOTIFICATION_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    notification_ref.delete()
                    data["success"] = True
                    data["message"] = "NOTIFICATION deleted"
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/personal/notification/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        temp = dict()

        data["Allow"] = "GET DELETE OPTIONS".split()

        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()

        data["name"] = "Notification"

        temp["GET"] = None
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
