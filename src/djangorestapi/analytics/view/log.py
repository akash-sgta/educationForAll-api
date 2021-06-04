from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from datetime import datetime, timedelta

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from analytics.models import Log
from analytics.serializer import Log_Serializer

# ------------------------------------------------------------


class Log_View(APIView):  # FIX : EXPERIMENTAL

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def get(self, request, dd=None, mm=None, yyyy=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if dd not in (None, "") and mm not in (None, "") and yyyy not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if not isAuthorizedUSER[0]:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                data["success"] = True
                date = f"{dd}-{mm}-{yyyy}"
                data["data"] = Log_Serializer(
                    Log.objects.filter(made_date__contains=date, api_token_ref=isAuthorizedAPI[1]).order_by("-pk"),
                    many=True,
                ).data
                return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/analytics/log/dd/mm/yyyy"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, dd=None, mm=None, yyyy=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if yyyy not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if not isAuthorizedUSER[0]:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if am_I_Authorized(request, "ADMIN") < 1:
                    data["success"] = False
                    data["message"] = f"USER_NOT_ADMIN"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if int(yyyy) == 0:
                        Log.all().delete()
                        data["success"] = True
                        data["message"] = "All Logs Cleared"
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            log_ref = Log.objects.get(pk=int(yyyy))
                        except Log.DoesNotExist:
                            data["success"] = False
                            data["message"] = "Invalid Log Id"
                            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            log_ref.delete()
                            data["success"] = True
                            data["message"] = "ADMIN : Log Cleared"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/analytics/log///id"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, dd=None, mm=None, yyyy=None):
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

        data["name"] = "Log"

        temp["GET"] = None
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
