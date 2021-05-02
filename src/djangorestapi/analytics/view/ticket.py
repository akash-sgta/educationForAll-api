from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from analytics.models import (
        Ticket
    )
from analytics.serializer import (
        Ticket_Serializer
    )

# ------------------------------------------------------------

class Ticket_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()
    
    def post(self, request, pk=None):
        data = dict()
        isAuthorizedUSER = am_I_Authorized(request, "USER")
        if(isAuthorizedUSER[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            ticket_de_serialized = Ticket_Serializer(data = request.data)
            ticket_de_serialized.initial_data['user_credential_id'] = isAuthorizedUSER[1]
            if(ticket_de_serialized.is_valid()):
                ticket_de_serialized.save()
                data['success'] = True
                data['data'] = ticket_de_serialized.data
                return Response(data = data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = ticket_de_serialized.errors
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
        data = dict()
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # pk    -   0   -   all
                # pk    -   1   -   unsolved
                # pk    -   2   -   solved
                isAuthorizedADMIN = am_I_Authorized(request, "admin")
                if(isAuthorizedADMIN > 0):
                    pk = int(pk)
                    if(pk == 0):
                        data['success'] = True
                        data['data'] = Ticket_Serializer(Ticket.objects.all(), many=True).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    elif(pk == 1):
                        data['success'] = True
                        data['data'] = Ticket_Serializer(Ticket.objects.filter(prime=False), many=True).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    elif(pk == 2):
                        data['success'] = True
                        data['data'] = Ticket_Serializer(Ticket.objects.filter(prime=True), many=True).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "item is invalid, only 0 1 2 allowed"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data['success'] = False
                    data['message'] = "ADMIN_NOT_AUTHORIZED"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/analytics/ticket/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
   
    def delete(self, request, pk=None):
        data = dict()
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                isAuthorizedADMIN = am_I_Authorized(request, "admin")
                if(isAuthorizedADMIN > 0):
                    pk = int(pk)
                    if(pk == 0):
                        Ticket.objects.all().delete()
                        data['success'] = True
                        data['message'] = "All TICKET(s) deleted"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            ticket_ref = Ticket.objects.get(ticket_id = pk)
                        except Ticket.DoesNotExist:
                            data['success'] = False
                            data['message'] = "item does not exist"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            ticket_ref.delete()
                            data['success'] = True
                            data['data'] = "TICKET deleted"
                            return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    data['success'] = False
                    data['message'] = "ADMIN_NOT_AUTHORIZED"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/analytics/ticket/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)


