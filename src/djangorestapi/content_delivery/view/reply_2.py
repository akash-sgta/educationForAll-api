from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from content_delivery.models import (
        Coordinator,
        ReplyToReply
    )
from content_delivery.serializer import (
        ReplyToReply_Serializer
    )

# ------------------------------------------------------------

class Reply_2_View(APIView):

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
            reply_de_serialized = ReplyToReply_Serializer(data = request.data)
            reply_de_serialized.initial_data['user_credential_id'] = isAuthorizedUSER[1]
            if(reply_de_serialized.is_valid()):
                reply_de_serialized.save()
                data['success'] = True
                data['data'] = reply_de_serialized.data
                return Response(data = data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = reply_de_serialized.errors
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
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = isAuthorizedUSER[1]
                if(int(pk) == 0):
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    try:
                        reply_ref = ReplyToReply.objects.filter(reply_to_id = int(pk))
                    except ReplyToReply.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data['success'] = True
                        data['data'] = ReplyToReply_Serializer(reply_ref, many=True).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/content/replyD/<parent_reply_id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
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
                try:
                    reply_ref = ReplyToReply.objects.get(reply_id = int(pk), user_credential_id=isAuthorizedUSER[1])
                except ReplyToReply.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist or does not belong to user"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    reply_de_serialized = ReplyToReply_Serializer(reply_ref, data=request.data)
                    if(reply_de_serialized.is_valid()):
                        reply_de_serialized.save()
                        data['success'] = True
                        data['data'] = reply_de_serialized.data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = reply_de_serialized.errors
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/content/replyD/<deep_reply_id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
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
                user_id = isAuthorizedUSER[1]
                if(int(pk) == 0): #all
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                    if(len(coordinator_ref) < 1):
                        data['success'] = False
                        data['message'] = "USER not COORDINATOR"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        ReplyToReply.objects.all().delete()
                        data['success'] = True
                        data['message'] = "All DEEP REPL(y/ies) deleted as COORDINATOR"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    try:
                        reply_ref = ReplyToReply.objects.get(reply_id = int(pk), user_credential_id = isAuthorizedUSER[1])
                    except ReplyToReply.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist or does not belong to user"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        reply_ref.delete()
                        data['success'] = True
                        data['message'] = "DEEP REPLY deleted"
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/content/replyD/<deep_reply_id>'
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
        
        data["name"] = "Reply_Deep"
        
        temp["POST"] = {
                "reply_to_id" : "Number",
                "reply_body" : "String"
            }
        temp["GET"] = None
        temp["PUT"] = {
                "reply_to_id" : "Number",
                "reply_body" : "String"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
