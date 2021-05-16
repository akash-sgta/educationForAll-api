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

from user_personal.models import (
    Enroll
)
# ------------------------------------------------------------

class Coordinator_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None): # TODO : Only Admins with CAGP privileges can create coordinators
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        isAuthorizedUSER = am_I_Authorized(request, "USER")
        if(isAuthorizedUSER[0] == False):
            data['success'] = False
            data['message'] = f"USER_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
            if(isAuthorizedADMIN < 1):
                data['success'] = False
                data['message'] = "USER_NOT_ADMIN"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(not do_I_Have_Privilege(request, "CAGP")):
                    data['success'] = False
                    data['message'] = "ADMIN_DOES_NOT_HAVE_CAGP_PRIVILEGE"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        coordinator_ref = Coordinator.objects.get(user_credential_id = int(request.data['user_id']))
                    except Coordinator.DoesNotExist:
                        try:
                            user_cred_ref = User_Credential.objects.get(user_credential_id = int(int(request.data['user_id'])))
                        except User_Credential.DoesNotExist:
                            data['success'] = False
                            data['message'] = "INVALID_USER_ID"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            coordinator_ref_new = Coordinator(user_credential_id = user_cred_ref)
                            coordinator_ref_new.save()
                            data['success'] = True
                            data['data'] = Coordinator_Serializer(coordinator_ref_new, many=False).data
                            return Response(data = data, status=status.HTTP_201_CREATED)
                    except KeyError or ValueError:
                        data['success'] = False
                        data['message'] = "CHECK_KEY_USER_ID"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data['success'] = True
                        data['message'] = "USER_ALREADY_COORDINATOR"
                        data['data'] = Coordinator_Serializer(coordinator_ref[0], many=False).data
                        return Response(data = data, status=status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"USER_NOT_AUTHORIZED"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(int(pk) == 0): # TODO : User checks if self is coordinator
                    try:
                        coordinator_ref = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1])
                    except Coordinator.DoesNotExist:
                        data['success'] = False
                        data['message'] = "INVALID_COORDINATOR_ID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        many_to_many = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_ref.coordinator_id)
                        subject_list = list()
                        for one in many_to_many:
                            subject_list.append(one.subject_id.subject_id)
                        data['success'] = True
                        data['data'] = {
                            "coordinator" : Coordinator_Serializer(coordinator_ref, many=False).data,
                            "subject" : subject_list.copy()
                        }
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                elif(int(pk) == 87795962440396049328460600526719): # TODO : Admin looks for all coordinator
                    isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                    if(isAuthorizedADMIN < 1):
                        data['success'] = False
                        data['message'] = "USER_NOT_ADMIN"
                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        coordinator_ref_all = Coordinator.objects.all()
                        data['data'] = list()
                        for coordinator_ref in coordinator_ref_all:
                            many_to_many = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_ref.coordinator_id).values('subject_id')
                            subject_list = [one['subject_id'] for one in many_to_many]
                            data['data'].append({
                                "coordinator" : Coordinator_Serializer(coordinator_ref, many=False).data,
                                "subject" : subject_list.copy()
                            })
                        data['success'] = True
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                elif(int(pk) == 13416989436929794359012690353783): # TODO : User looks for all coordinators under enrolled subjects
                    enrolled_subjects = Enroll.objects.filter(user_credential_id = isAuthorizedUSER[1]).values('subject_id')
                    data['data'] = dict()
                    for enroll in enrolled_subjects:
                        coordinators_for_subject = Subject_Coordinator_Int.objects.filter(subject_id = enroll['subject_id'])
                        data['data'][enroll['subject_id']] = list()
                        for coordinator in coordinators_for_subject:
                            data['data'][enroll['subject_id']].append(Coordinator_Serializer(coordinator.coordinator_id, many=False).data)
                    data['success'] = True
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else: # TODO : User looks for specific coordinator
                    try:
                        coordinator_ref = Coordinator.objects.get(user_credential_id = int(pk))
                    except Coordinator.DoesNotExist:
                        data['success'] = False
                        data['message'] = "INVALID_COORDINATOR_ID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        many_to_many = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_ref.coordinator_id).values('subject_id')
                        subject_list = [one['subject_id'] for one in many_to_many]
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
    
    def put(self, request, pk=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"USER_NOT_AUTHORIZED"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(int(pk) == 0): # TODO : Self Coordinators can get or revoke subject privileges
                    try:
                        coordinator_ref = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1])
                    except Coordinator.DoesNotExist:
                        data['success'] = False
                        data['message'] = "USER_NOT_COORDINATOR"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        id = request.data['subject_id']
                        add_Subject = True
                        try:
                            id = int(id)
                            if(id < 0):
                                id = id*-1
                                add_Subject = False
                            subject_ref = Subject.objects.get(subject_id = id)
                        except Subject.DoesNotExist or ValueError or TypeError:
                            data['success'] = False
                            data['message'] = "SUBJECT_ID_INVALID"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            if(not add_Subject): # TODO : Revoking access from subject
                                try:
                                    many_to_many = Subject_Coordinator_Int.objects.get(
                                                        subject_id = subject_ref.subject_id,
                                                        coordinator_id = coordinator_ref.coordinator_id
                                                    )
                                except Subject_Coordinator_Int.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = "SUBJECT_DOES_NOT_BELONG_TO_COORDINATOR"
                                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    many_to_many.delete()
                                    data['success'] = True
                                    data['message'] = "SUBJECT_REMOVED_FROM_COORDINATOR"
                                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                            else: # TODO : Granting access to subject
                                try:
                                    many_to_many = Subject_Coordinator_Int.objects.get(
                                                        subject_id = subject_ref.subject_id,
                                                        coordinator_id = coordinator_ref.coordinator_id
                                                    )
                                except Subject_Coordinator_Int.DoesNotExist:
                                    Subject_Coordinator_Int(subject_id = subject_ref, coordinator_id = coordinator_ref).save()
                                    data['success'] = True
                                    data['message'] = "SUBJECT_ADDED_TO_COORDINATOR"
                                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                else:
                                    data['success'] = False
                                    data['message'] = "SUBJECT_ALREADY_BELONGS_TO_COORDINATOR"
                                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else: # TODO : Admin with CAGP changing access of other coordinators
                    if(am_I_Authorized(request, "ADMIN") < 1):
                        data['success'] = False
                        data['message'] = f"USER_NOT_ADMIN"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        if(not do_I_Have_Privilege(request, "CAGP")):
                            data['success'] = False
                            data['message'] = f"ADMIN_DOES_NOT_HAVE_CAGP_PRIVILEGE"
                            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            try:
                                coordinator_ref = Coordinator.objects.get(user_credential_id = int(pk))
                            except Coordinator.DoesNotExist:
                                data['success'] = False
                                data['message'] = "ADMIN : INVALID_COORDINATOR_ID"
                                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                try:
                                    id = request.data['subject_id']
                                except KeyError:
                                    data['success'] = False
                                    data['message'] = "CHECK_SUBJECT_ID"
                                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    add_Subject = True
                                    try:
                                        id = int(id)
                                        if(id < 0):
                                            id = id*-1
                                            add_Subject = False
                                        subject_ref = Subject.objects.get(subject_id = id)
                                    except Subject.DoesNotExist or ValueError or TypeError:
                                        data['success'] = False
                                        data['message'] = "ADMIN : SUBJECT_ID_INVALID"
                                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                                    else:
                                        if(not add_Subject): # TODO : Revoking access from subject
                                            try:
                                                many_to_many = Subject_Coordinator_Int.objects.get(
                                                                    subject_id = subject_ref.subject_id,
                                                                    coordinator_id = coordinator_ref.coordinator_id
                                                                )
                                            except Subject_Coordinator_Int.DoesNotExist:
                                                data['success'] = False
                                                data['message'] = "ADMIN : SUBJECT_DOES_NOT_BELONG_TO_COORDINATOR"
                                                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                                            else:
                                                many_to_many.delete()
                                                data['success'] = True
                                                data['message'] = "ADMIN : SUBJECT_REMOVED_FROM_COORDINATOR"
                                                return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                        else: # TODO : Granting access to subject
                                            try:
                                                many_to_many = Subject_Coordinator_Int.objects.get(
                                                                    subject_id = subject_ref.subject_id,
                                                                    coordinator_id = coordinator_ref.coordinator_id
                                                                )
                                            except Subject_Coordinator_Int.DoesNotExist:
                                                Subject_Coordinator_Int(subject_id = subject_ref, coordinator_id = coordinator_ref).save()
                                                data['success'] = True
                                                data['message'] = "ADMIN : SUBJECT_ADDED_TO_COORDINATOR"
                                                return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                            else:
                                                data['success'] = False
                                                data['message'] = "ADMIN : SUBJECT_ALREADY_BELONGS_TO_COORDINATOR"
                                                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/content/coordinator/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"USER_NOT_AUTHORIZED"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(int(pk) == 0):
                    try:
                        coordinator_ref = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1])
                    except Coordinator.DoesNotExist:
                        data['success'] = False
                        data['message'] = "USER_NOT_COORDINATOR"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        coordinator_ref.delete()
                        data['success'] = True
                        data['message'] = "USER_NOT_COORDINATOR_ANYMORE"
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                elif(int(pk) == 87795962440396049328460600526719): # TODO : Admin with CAGP access deleting all coordinators
                    if(am_I_Authorized(request, "ADMIN") < 1):
                        data['success'] = False
                        data['message'] = f"USER_NOT_ADMIN"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        if(not do_I_Have_Privilege(request, "CAGP")):
                            data['success'] = False
                            data['message'] = f"ADMIN_DOES_NOT_HAVE_CAGP_PRIVILEGE"
                            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            Coordinator.objects.all().delete()
                            data['success'] = True
                            data['message'] = f"ADMIN : ALL_COORDINATORS_DELETED"
                            return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else: # TODO : Admin with CAGP access deleting specific coordinators
                    if(am_I_Authorized(request, "ADMIN") < 1):
                        data['success'] = False
                        data['message'] = f"USER_NOT_ADMIN"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        if(not do_I_Have_Privilege(request, "CAGP")):
                            data['success'] = False
                            data['message'] = f"ADMIN_DOES_NOT_HAVE_CAGP_PRIVILEGE"
                            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            try:
                                coordinator_ref = Coordinator.objects.get(user_credential_id = int(pk))
                            except Coordinator.DoesNotExist:
                                data['success'] = False
                                data['message'] = "ADMIN : INVALID_COORDINATOR_ID"
                                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                coordinator_ref.delete()
                                data['success'] = True
                                data['message'] = f"ADMIN : COORDINATOR_DELETED"
                                return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/content/coordinator/<id>'
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
        
        data["name"] = "Coordinator"
        
        temp["POST"] = {
                "user_id" : "Number"
            }
        temp["GET"] = None
        temp["PUT"] = {
                "subject" : "Number"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
