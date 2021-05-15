from django.http.response import JsonResponse

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from content_delivery.models import (
        Coordinator,
        Subject,
        Subject_Coordinator_Int,
    )
from content_delivery.serializer import (
        Subject_Serializer,
    )

from auth_prime.important_modules import (
        am_I_Authorized,
    )

# ------------------------------------------------------------

class Subject_View(APIView):

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
            coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                subject_de_serialized = Subject_Serializer(data = request.data)
                details = " ".join([word.upper() for word in subject_de_serialized.initial_data['subject_name'].split()])
                subject_ref = Subject.objects.filter(subject_name__icontains = details)
                if(len(subject_ref) > 0):
                    data['success'] = True
                    data['message'] = "SUBJECT already exists"
                    data['data'] = Subject_Serializer(subject_ref[0], many=False).data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    subject_de_serialized.initial_data['subject_name'] = details
                    if(subject_de_serialized.is_valid()):
                        subject_de_serialized.save()
                        data['success'] = True
                        data['data'] = subject_de_serialized.data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = subject_de_serialized.errors
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
                if(int(pk) == 2312951593774859): # FIXME: Universal asking for all subjects
                    data['data'] = Subject_Serializer(Subject.objects.all(), many=True).data
                    data['success'] = True
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                elif(int(pk) == 6878134053606367): # FIXME: Coordinator asking for subjects to form post
                    try:
                        am_I_Coordinator = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1])
                    except Coordinator.DoesNotExist:
                        data['success'] = True
                        data['message'] = "USER not a COORINATOR"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        subject_coor_int = Subject_Coordinator_Int.objects.filter(coordinator_id = am_I_Coordinator)
                        subjects = [ref.subject_id for ref in subject_coor_int]
                        data['data'] = Subject_Serializer(subjects, many=True).data
                    data['success'] = True
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    try:
                        subject_ref = Subject.objects.get(subject_id = int(pk))
                    except Subject.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data['success'] = True
                        data['data'] = Subject_Serializer(subject_ref, many=False).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/content/subject/<id>'
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
                coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                if(len(coordinator_ref) < 1):
                    data['success'] = False
                    data['message'] = "USER not COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        subject_ref = Subject.objects.get(subject_id = int(pk))
                    except Subject.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        subject_de_serialized = Subject_Serializer(subject_ref, data=request.data)
                        details = " ".join([word.upper() for word in subject_de_serialized.initial_data['subject_name'].split()])
                        subject_ref = Subject.objects.filter(subject_name__icontains = details)
                        if(len(subject_ref) > 0 and subject_ref[0].subject_id != int(pk)):
                            data['success'] = False
                            data['message'] = "SUBJECT name already in use"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            subject_de_serialized.initial_data['subject_name'] = details
                            if(subject_de_serialized.is_valid()):
                                subject_de_serialized.save()
                                data['success'] = True
                                data['data'] = subject_de_serialized.data
                                return Response(data = data, status=status.HTTP_201_CREATED)
                            else:
                                data['success'] = False
                                data['message'] = subject_de_serialized.errors
                                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/content/subject/<id>'
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
                coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                if(len(coordinator_ref) < 1):
                    data['success'] = False
                    data['message'] = "USER not COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if(int(pk) == 0): #all
                        Subject.objects.all().delete()
                        data['success'] = True
                        data['message'] = "All SUBJECT(s) deleted"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            subject_ref = Subject.objects.get(subject_id = int(pk))
                        except Subject.DoesNotExist:
                            data['success'] = False
                            data['message'] = "item does not exist"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            subject_ref.delete()
                            data['success'] = True
                            data['message'] = "SUBJECT deleted"
                            return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/content/subject/<id>'
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
        
        data["name"] = "Subject"
        
        temp["POST"] = {
                "subject_name" : "String",
                "subject_description" : "String"
            }
        temp["GET"] = None
        temp["PUT"] = {
                "subject_name" : "String",
                "subject_description" : "String"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
