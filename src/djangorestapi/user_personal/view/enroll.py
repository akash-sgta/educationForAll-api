from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from user_personal.models import (
        Enroll
    )
from user_personal.serializer import (
        Enroll_Serializer
    )

from content_delivery.models import (
        Coordinator,
        Subject_Coordinator_Int
    )

# ------------------------------------------------------------

class Enroll_View(APIView):

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
            try:
                enroll_ref = Enroll.objects.get(user_credential_id = isAuthorizedUSER[1], subject_id = request.data['subject_id'])
            except Enroll.DoesNotExist:
                enroll_serialized = Enroll_Serializer(data = request.data)
                enroll_serialized.initial_data['user_credential_id'] = int(isAuthorizedUSER[1])
                if(enroll_serialized.is_valid()):
                    enroll_serialized.save()
                    data['success'] = True
                    data['data'] = enroll_serialized.data
                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = f"error:SERIALIZING_ERROR, message:{enroll_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['success'] = True
                data['message'] = f"User already enrolled with subject"
                data['data'] = Enroll_Serializer(enroll_ref, many=False).data
                return Response(data = data, status=status.HTTP_202_ACCEPTED)

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
                try:
                    # coordinator   -   0   -   All enrollment under thier subject
                    # others        -   0   -   All subjects enrolled
                    if(int(pk) == 0):
                        coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                        if(len(coordinator_ref) < 1): # normal user
                            data['success'] = True
                            subject_list = list()
                            for one in Enroll_Serializer(Enroll.objects.filter(user_credential_id = isAuthorizedUSER[1]), many=True).data:
                                subject_list.append(one['subject_id'])
                            data['data'] = {'subject' : subject_list.copy()}
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else: # coordinator
                            coordinator_ref = coordinator_ref[0]
                            many_to_many_coor_sub = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_ref.coordinator_id)
                            # print(many_to_many_coor_sub)
                            enroll_list = list()
                            for one in many_to_many_coor_sub:
                                user_list = list()
                                enroll_ref = Enroll.objects.filter(subject_id = one.subject_id.subject_id)
                                for enroll in enroll_ref:
                                    user_list.append(enroll.user_credential_id.user_credential_id)
                                enroll_list.append({
                                    "subject" : one.subject_id.subject_id,
                                    "user" : user_list.copy()
                                })
                            data['success'] = True
                            data['data'] = enroll_list.copy()
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "only 0 accepted as id"
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/personal/enroll/<id>'
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
                try:
                    enroll_ref = Enroll.objects.get(user_credential_id = isAuthorizedUSER[1], subject_id = pk)
                except Enroll.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist or does not belong to user"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    enroll_ref.delete()
                    data['success'] = True
                    data['message'] = "ENROLLMENT deleted"
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/personal/enroll/<id>'
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

        data["Allow"] = "POST GET DELETE OPTIONS".split()
        
        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()
        
        data["name"] = "Enroll"
        
        temp["POST"] = {
            "subject_id" : "Number"
        }
        temp["GET"] = None
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
