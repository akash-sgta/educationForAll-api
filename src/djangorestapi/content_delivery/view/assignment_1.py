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
        Assignment,
        Subject_Coordinator_Int,
        Post,
    )
from content_delivery.serializer import (
        Assignment_Serializer
    )
    
from user_personal.models import (
    Assignment_Submission_Int,
    Enroll,
)

# ------------------------------------------------------------

class Assignment_1_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()
    
    def post(self, request, pk=None): # TODO : Only Coordinator can create assignment
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
            try:
                coordinator_ref = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1])
            except Coordinator.DoesNotExist:
                data['success'] = False
                data['message'] = "USER_NOT_COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                assignment_de_serialized = Assignment_Serializer(data = request.data)
                if(assignment_de_serialized.is_valid()):
                    assignment_de_serialized.save()
                    data['success'] = True
                    data['data'] = assignment_de_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = assignment_de_serialized.errors
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
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
                if(int(pk) == 87795962440396049328460600526719): # TODO : User can see all assignments respect to enrolled subjects
                    enroll = Enroll.objects.filter(user_credential_id = isAuthorizedUSER[1]).values('subject_id')
                    subject_list = [int(sub['subject_id']) for sub in enroll]
                    post_ref = Post.object.filter(subject_id__in = subject_list)
                    data['success'] = True
                    data['data'] = list()
                    for post in post_ref:
                        if(post.assignment_id != None):
                            assignment_ref = post.assignment_id
                            data['data'].append({
                                "assignment" : Assignment_Serializer(assignment_ref, many=False).data,
                                "submission" : [one['submission_id'] for one in Assignment_Submission_Int.objects.filter(assignment_id = assignment_ref.assignment_id).values('submission_id')]
                            })
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                elif(int(pk) == 0): # TODO : Coordinator looks for assignments under them
                    try:
                        coordinator_id = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1]).coordinator_id
                    except Coordinator.DoesNotExist:
                        data['success'] = False
                        data['message'] = "USER_NOT_COORDINATOR"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        coordinator_subjects = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_id).values('subject_id')
                        subject_list = [int(sub['subject_id']) for sub in coordinator_subjects]
                        post_ref = Post.object.filter(subject_id__in = subject_list)
                        data['success'] = True
                        data['data'] = list()
                        for post in post_ref:
                            if(post.assignment_id != None):
                                assignment_ref = post.assignment_id
                                data['data'].append({
                                    "assignment" : Assignment_Serializer(assignment_ref, many=False).data,
                                    "submission" : [one['submission_id'] for one in Assignment_Submission_Int.objects.filter(assignment_id = assignment_ref.assignment_id).values('submission_id')]
                                })
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else: # TODO : Any user looking for assignment
                    try:
                        assignment_ref = Assignment.objects.get(assignment_id = int(pk))
                    except Assignment.DoesNotExist:
                        data['success'] = False
                        data['message'] = "INVALID_ASSIGNMENT_ID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data['success'] = True
                        data['data'] = {
                            "assignment" : Assignment_Serializer(assignment_ref, many=False).data,
                            "submission" : [one["subject_id"] for one in Assignment_Submission_Int.objects.filter(assignment_id = assignment_serializer['assignment_id']).values('subject_id')]
                        }
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/content/assignment/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None): # TODO : Only Coordinator can edit assignment
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
                try:
                    coordinator_ref = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1])
                except Coordinator.DoesNotExist:
                    data['success'] = False
                    data['message'] = "USER_NOT_COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        assignment_ref = Assignment.objects.get(assignment_id = int(pk))
                    except Assignment.DoesNotExist:
                        data['success'] = False
                        data['message'] = "INVALID_ASSIGNMENT_ID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        assignment_de_serialized = Assignment_Serializer(assignment_ref, data=request.data)
                        if(assignment_de_serialized.is_valid()):
                            assignment_de_serialized.save()
                            data['success'] = True
                            data['data'] = assignment_de_serialized.data
                            return Response(data = data, status=status.HTTP_201_CREATED)
                        else:
                            data['success'] = False
                            data['message'] = assignment_de_serialized.errors
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/content/assignment/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None): # TODO : Only Coordinator can delete assignment
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
                try:
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                except Coordinator.DoesNotExist:
                    data['success'] = False
                    data['message'] = "USER_NOT_COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        assignment_ref = Assignment.objects.get(assignment_id = int(pk))
                    except Assignment.DoesNotExist:
                        data['success'] = False
                        data['message'] = "INVALID_ASSIGNMENT_ID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        assignment_ref.delete()
                        data['success'] = True
                        data['message'] = "ASSIGNMENT_DELETED"
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/content/assignment/<id>'
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
        
        data["name"] = "Assignment"
        
        temp["POST"] = {
                "assignment_name" : "String",
                "assignment_body" : "String",
                "assignment_external_url_1" : "URL/null",
                "assignment_external_url_2" : "URL/null"
            }
        temp["GET"] = None
        temp["PUT"] = {
                "assignment_name" : "String",
                "assignment_body" : "String",
                "assignment_external_url_1" : "URL/null",
                "assignment_external_url_2" : "URL/null"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
