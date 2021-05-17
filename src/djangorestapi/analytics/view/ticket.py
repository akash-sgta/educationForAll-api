from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from analytics.models import Ticket
from analytics.serializer import Ticket_Serializer

# ------------------------------------------------------------


class Ticket_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None):  # TODO : Any user can post tickets
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
            ticket_de_serialized = Ticket_Serializer(data=request.data)
            ticket_de_serialized.initial_data["user_ref"] = isAuthorizedUSER[1]
            if ticket_de_serialized.is_valid():
                ticket_de_serialized.save()
                data["success"] = True
                data["data"] = ticket_de_serialized.data
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data["success"] = False
                data["message"] = ticket_de_serialized.errors
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):  # TODO : Only Admins can access tickets
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
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if isAuthorizedADMIN > 0:
                    pk = int(pk)
                    if pk == 0:  # TODO : All tickets
                        data["success"] = True
                        data["data"] = Ticket_Serializer(Ticket.objects.all().order_by("-pk"), many=True).data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif pk == 87795962440396049328460600526719:  # TODO : Unsolved Tickets
                        data["success"] = True
                        data["data"] = Ticket_Serializer(Ticket.objects.filter(prime=False).order_by("-pk"), many=True).data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif pk == 13416989436929794359012690353783:  # TODO : Solved Tickets
                        data["success"] = True
                        data["data"] = Ticket_Serializer(Ticket.objects.filter(prime=True).order_by("-pk"), many=True).data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            ticket_ref = Ticket.objects.get(pk=pk)
                        except Ticket.DoesNotExist:
                            data["success"] = False
                            data["message"] = "INVALID_TICKET_ID"
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data["success"] = True
                            data["data"] = Ticket_Serializer(ticket_ref, many=False).data
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:
                    data["success"] = False
                    data["message"] = "USER_NOT_ADMIN"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/analytics/ticket/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):  # TODO : Only Admins can change Ticket status
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
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if isAuthorizedADMIN < 1:
                    data["success"] = False
                    data["message"] = f"USER_NOT_ADMIN"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        ticket_ref = Ticket.objects.get(pk=int(pk))
                    except Ticket.DoesNotExist:
                        data["success"] = False
                        data["message"] = "TICKET_ID_INVALID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        try:
                            ticket_ref.prime = request.data["solved"]
                            ticket_ref.save()
                        except Exception as ex:
                            data["success"] = False
                            data["message"] = "INVALID_JSON_DATA[true/false]"
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data["success"] = True
                            data["data"] = Ticket_Serializer(ticket_ref, many=False).data
                            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/analytics/ticket/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):  # TODO : Only Admins can delete Tickets
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
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if isAuthorizedADMIN > 0:
                    pk = int(pk)
                    if pk == 87795962440396049328460600526719:
                        Ticket.objects.all().delete()
                        data["success"] = True
                        data["message"] = "ALL_TICKETS_DELETED"
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            ticket_ref = Ticket.objects.get(pk=pk)
                        except Ticket.DoesNotExist:
                            data["success"] = False
                            data["message"] = "TICKET_ID_INVALID"
                            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            ticket_ref.delete()
                            data["success"] = True
                            data["data"] = "TICKET_DELETED"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:
                    data["success"] = False
                    data["message"] = "USER_NOT_ADMIN"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/analytics/ticket/<id>"}
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

        data["name"] = "Token"

        temp["POST"] = {"body": "String : unl"}
        temp["GET"] = None
        temp["PUT"] = {"prime": "Boolean"}
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
