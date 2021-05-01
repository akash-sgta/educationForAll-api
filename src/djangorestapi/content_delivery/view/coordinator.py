from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
        do_I_Have_Privilege
    )

from content_delivery.models import (
        Coordinator,
        Subject_Coordinator_Int,
        Subject
    )
from content_delivery.serializer import (
        Coordinator_Serializer
    )

from auth_prime.models import (
        User_Credential
    )

# ------------------------------------------------------------

class Coordinator_View(APIView):

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
            isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
            if(isAuthorizedADMIN < 2):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                isCoordinator = do_I_Have_Privilege(request, "CAGP")
                if(not isCoordinator):
                    data['success'] = False
                    data['message'] = "ADMIN does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    id = request.data['user_id']
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(id))
                    if(len(coordinator_ref) > 0):
                        data['success'] = True
                        data['message'] = "USER already COORDINATOR"
                        data['data'] = Coordinator_Serializer(coordinator_ref[0], many=False).data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        try:
                            user_cred_ref = User_Credential.objects.get(user_credential_id = int(id))
                        except User_Credential.DoesNotExist:
                            data['success'] = False
                            data['message'] = "item invalid"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            coordinator_ref_new = Coordinator(user_credential_id = user_cred_ref)
                            coordinator_ref_new.save()
                            data['success'] = True
                            data['data'] = Coordinator_Serializer(coordinator_ref_new, many=False).data
                            return Response(data = data, status=status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        data = dict()
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = isAuthorizedUSER[1]
                if(int(pk) == 0): # pull all coordinator data
                    coordinator_ref_all = Coordinator.objects.all()
                    coordinator_list = list()
                    for coordinator_ref in coordinator_ref_all:
                        many_to_many = Subject_Coordinator_Int.objects.filter(
                                            coordinator_id = coordinator_ref.coordinator_id
                                        )
                        subject_list = list()
                        for one in many_to_many:
                            subject_list.append(one.subject_id.subject_id)
                        coordinator_list.append({
                            "coordinator" : Coordinator_Serializer(coordinator_ref, many=False).data,
                            "subject" : subject_list.copy()
                            })
                    data['success'] = True
                    data['data'] = coordinator_list.copy()
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    try:
                        coordinator_ref = Coordinator.objects.get(coordinator_id = int(pk))
                    except Coordinator.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        many_to_many = Subject_Coordinator_Int.objects.filter(coordinator_id = int(pk))
                        subject_list = list()
                        for one in many_to_many:
                            subject_list.append(one.subject_id.subject_id)
                        data['success'] = True
                        data['data'] = {
                            "coordinator" : Coordinator_Serializer(coordinator_ref, many=False).data,
                            "subject" : subject_list.copy()
                        }
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/content/coordinator/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def edit(self, request, pk=None):
        data = dict()
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if(isAuthorizedADMIN < 2):
                    data['success'] = False
                    data['message'] = "USER does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    isCoordinator = do_I_Have_Privilege(request, "CAGP")
                    if(not isCoordinator):
                        data['success'] = False
                        data['message'] = "ADMIN does not have required ADMIN PRIVILEGES"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        id = request.data['subject']
                        addS = True
                        try:
                            id = int(id)
                            if(id < 0):
                                id = id*-1
                                addS = False
                            subject_ref = Subject.objects.get(subject_id = id)
                        except Subject.DoesNotExist:
                            data['success'] = False
                            data['message'] = "SUBJECT id Invalid"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        except ValueError or TypeError:
                            data['success'] = False
                            data['message'] = "Invalid id"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            try:
                                coordinator_ref = Coordinator.objects.get(coordinator_id = int(pk))
                            except Coordinator.DoesNotExist:
                                data['success'] = False
                                data['message'] = "item does not exist"
                                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                if(not addS): # revoke
                                    try:
                                        many_to_many = Subject_Coordinator_Int.objects.get(
                                                            subject_id = subject_ref.subject_id,
                                                            coordinator_id = coordinator_ref.coordinator_id
                                                        )
                                    except Subject_Coordinator_Int.DoesNotExist:
                                        data['success'] = True
                                        data['message'] = "SUBJECT not belong to COORDINATOR"
                                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                    else:
                                        many_to_many.delete()
                                        data['success'] = True
                                        data['message'] = "SUBJECT removed from COORDINATOR"
                                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                else: # grant
                                    try:
                                        many_to_many = Subject_Coordinator_Int.objects.get(
                                                            subject_id = subject_ref.subject_id,
                                                            coordinator_id = coordinator_ref.coordinator_id
                                                        )
                                    except Subject_Coordinator_Int.DoesNotExist:
                                        Subject_Coordinator_Int(subject_id = subject_ref, coordinator_id = coordinator_ref).save()
                                        data['success'] = True
                                        data['message'] = "SUBJECT added to COORDINATOR"
                                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                    else:
                                        data['success'] = True
                                        data['message'] = "SUBJECT already belong to COORDINATOR"
                                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/content/coordinator/<id>'
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
                user_id = isAuthorizedUSER[1]
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if(isAuthorizedADMIN < 2):
                    data['success'] = False
                    data['message'] = "USER does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    isPrivileged = do_I_Have_Privilege(request, "CAGP")
                    if(not isPrivileged):
                        if(int(pk) == 0): #all
                            Coordinator.objects.all().delete()
                            data['success'] = True
                            data['message'] = "All Coordinator(s) deleted"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            try:
                                coordinator_ref = Coordinator.objects.get(coordinator_id = int(pk))
                            except Coordinator.DoesNotExist:
                                data['success'] = False
                                data['message'] = "item does not exist"
                                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                coordinator_ref.delete()
                                data['success'] = True
                                return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "ADMIN does not have required ADMIN PRIVILEGES"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/content/coordinator/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)