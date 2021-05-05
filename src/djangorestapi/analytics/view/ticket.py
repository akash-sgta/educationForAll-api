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
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
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
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
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
                        data['message'] = "item is invalid, only 0(all) 1(solved) 2(unsolved) allowed"
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
    
    def put(self, request, pk=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
        if(isAuthorizedADMIN < 1):
            data['success'] = False
            data['message'] = f"error:USER_NOT_ADMIN"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                ticket_ref = Ticket.objects.get(ticket_id = int(pk))
            except Ticket.DoesNotExist:
                data['success'] = False
                data['message'] = 'id does not exist'
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    ticket_ref.prime = request.data['solved']
                    ticket_ref.save()
                except Exception as ex:
                    print("::", ex)
                    data['success'] = False
                    data['message'] = 'invalid data in json'
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data['success'] = True
                    data['data'] = Ticket_Serializer(ticket_ref, many=False).data
                    return Response(data = data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
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

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            
        temp = dict()

        data["Allow"] = "POST GET PUT DELETE OPTIONS".split()
        
        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()
        
        data["name"] = "Token"
        
        temp["POST"] = {
                "prime" : "Boolean"
            }
        temp["GET"] = None
        temp["POST"] = {
                "ticket_body" : "String"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)


