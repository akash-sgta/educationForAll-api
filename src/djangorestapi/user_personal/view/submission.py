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

from user_personal.models import (
        Submission,
        Assignment_Submission_Int
    )
from user_personal.serializer import (
        Submission_Serializer
    )

# ------------------------------------------------------------

class Submission_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None, pkk=None):
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
            submission_serialized = Submission_Serializer(data = request.data)
            submission_serialized.initial_data['user_credential_id'] = int(isAuthorizedUSER[1])
            try:
                assignment_id = submission_serialized.initial_data['assignment_id']
                assignment_ref = Assignment.objects.get(assignment_id = assignment_id)
            except Assignment.DoesNotExist:
                data['success'] = False
                data['message'] = "INVALID_ASSIGNMENT_ID"
                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
            else:
                if(submission_serialized.is_valid()):
                    submission_serialized.save()
                    submission_ref = Submission.objects.get(submission_id = submission_serialized.data['submission_id'])
                    many_to_many_new = Assignment_Submission_Int(
                        assignment_id = assignment_ref,
                        submission_id = submission_ref
                    )
                    many_to_many_new.save()
                    data['success'] = True
                    data['data'] = submission_serialized.data
                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = f"SERIALIZING_ERROR : {submission_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, pkk=None):
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
                try:
                    # /pk_1/pk_2
                    # pk_1 - 0, pk_2 - None    ->  User demanding all their submission
                    # pk_1 - x, pk_2 - None    ->  User demanding for submission [x]
                    # pk_1 - 0, pk_2 - x       ->  Coordiantor demanding all submission under assignment [x]
                    if(int(pk) == 0): # TODO : User accessing submission
                        if(int(pkk) == 0): # TODO : All submission
                            submission_ref = Submission.objects.filter(user_credential_id = isAuthorizedUSER[1]).values('submission_id')
                            submission_list = [one['submission_id'] for one in submission_serialized]
                            temp = list()
                            for sub in submission_list:
                                try:
                                    marks_ref = Assignment_Submission_Int.objects.get(submission_id = sub)
                                except Assignment_Submission_Int.DoesNotExist:
                                    pass
                                else:
                                    temp.append({
                                        "assignment_id" : marks_ref.assignment_id.assignment_id,
                                        "submission" : sub,
                                        "marks" : marks_ref.marks
                                    })
                            data['success'] = True
                            data['data'] = temp.copy()
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else: # TODO : Specific Submission
                            try:
                                submission_ref = Submission.objects.get(user_credential_id = isAuthorizedUSER[1], submission_id=int(pkk))
                            except Submission.DoesNotExist:
                                data['success'] = False
                                data['message'] = "INVALID_SUBMISSION_ID"
                                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                submission_serialized = Submission_Serializer(submission_ref, many=False).data
                                try:
                                    marks_ref = Assignment_Submission_Int.objects.get(submission_id = submission_serialized['submission_id'])
                                except Assignment_Submission_Int.DoesNotExist:
                                    pass # FIX : Why did this forgot
                                else:
                                    data['data'] = {
                                        "assignment_id" : marks_ref.assignment_id.assignment_id,
                                        "submission" : submission_serialized,
                                        "marks" : marks_ref.marks
                                    }
                                data['success'] = True
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif(int(pk) == 87795962440396049328460600526719): # TODO : Coordinator accessing submission
                        if(int(pkk) == 0): # TODO : All submission
                            try:
                                coordinator_id = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1]).coordinator_id
                            except Coordinator.DoesNotExist:
                                data['success'] = False
                                data['message'] = "USER_NOT_COORDINATOR"
                                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                subject_coordinator_ids = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_id).values('subject_id')
                                subject_ids = [int(one['subject_id']) for one in subject_coordinator_ids]
                                assignment_ids = Post.objects.filter(subject_id__in = subject_ids).values('assignment_id')
                                assignment_ids = [int(one['assignment_id']) for one in assignment_ids]
                                temp = dict()
                                for one in assignment_ids:
                                    marks_ref = Assignment_Submission_Int.objects.filter(assignment_id = one)
                                    temp[one] = list()
                                    for one_ref in marks_ref:
                                        temp[one].append({
                                            "submission_id" : one_ref.submission_id.submission_id,
                                            "marks" : marks_ref.marks
                                        })
                                data['success'] = False
                                data['data'] = temp.copy()
                                return Response(data=data, status=status.HTTP_200_OK)
                        else: # TODO : Specific Submission
                            try:
                                coordinator_id = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1]).coordinator_id
                            except Coordinator.DoesNotExist:
                                data['success'] = False
                                data['message'] = "USER_NOT_COORDINATOR"
                                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                try:
                                    submission_ref = Submission.objects.get(submission_id = int(pkk))
                                except Submission.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = "INVALID_SUBMISSION_ID"
                                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    marks_ref = Assignment_Submission_Int.objects.get(submission_id = submission_ref.submission_id)
                                    temp[one] = list()
                                    for one_ref in marks_ref:
                                        temp[one].append({
                                            "submission_id" : one_ref.submission_id.submission_id,
                                            "marks" : marks_ref.marks
                                        })
                                    data['success'] = True
                                    data['data'] = temp.copy()
                                    return Response(data=data, status=status.HTTP_200_OK)
                                    

                            
                    else: # TODO : Specific Submission
                            try:
                                submission_ref = Submission.objects.get(user_credential_id = isAuthorizedUSER[1], submission_id=int(pkk))
                            except Submission.DoesNotExist:
                                data['success'] = False
                                data['message'] = "INVALID_SUBMISSION_ID"
                                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                submission_serialized = Submission_Serializer(submission_ref, many=False).data
                                try:
                                    marks_ref = Assignment_Submission_Int.objects.get(submission_id = submission_serialized['submission_id'])
                                except Assignment_Submission_Int.DoesNotExist:
                                    data['data'] = {
                                        "assignment_id" : None,
                                        "submission" : submission_serialized,
                                        "marks" : marks_ref.marks
                                    }
                                else:
                                    data['data'] = {
                                        "assignment_id" : marks_ref.assignment_id.assignment_id,
                                        "submission" : submission_serialized,
                                        "marks" : marks_ref.marks
                                    }
                                data['success'] = True
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)

                            coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                            if(len(coordinator_ref) < 1):
                                data['success'] = False
                                data['message'] = "USER not COORDINATOR"
                                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                many_to_many_ref = Assignment_Submission_Int.objects.filter(assignment_id = int(pk_2))
                                temp = list()
                                for one in many_to_many_ref:
                                    submission_ref = Submission.objects.get(submission_id = one.submission_id.submission_id)
                                    submission_serialized = Submission_Serializer(submission_ref, many=False).data
                                    temp.append({
                                        "assignment_id" : None if(one.assignment_id == None) else one.assignment_id.assignment_id,
                                        "submission" : submission_serialized,
                                        "marks" : one.marks
                                    })
                                data['success'] = True
                                data['data'] = temp.copy()
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)        
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/personal/submission/<id_1>-<id_2>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk_1=None, pk_2=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        if(pk_1 not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    submission_ref = Submission.objects.get(user_credential_id = isAuthorizedUSER[1], submission_id = pk_1)
                except Submission.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist or does not belong to user"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    submission_serialized = Submission_Serializer(submission_ref, data=request.data)
                    submission_serialized.initial_data['user_credential_id'] = isAuthorizedUSER[1]
                    if(submission_serialized.is_valid()):
                        submission_serialized.save()
                        data['success'] = True
                        data['data'] = submission_serialized.data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = f"error:SERIALIZING_ERROR, message:{submission_serialized.errors}"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/personal/submission/<id>-'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk_1=None, pk_2=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        if(pk_1 not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    submission_ref = Submission.objects.get(user_credential_id = isAuthorizedUSER[1], submission_id = pk_1)                    
                except Submission.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist or does not belong to user"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    submission_ref.delete()
                    data['success'] = True
                    data['message'] = "SUBMISSION deleted"
                    return Response(data = data)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/personal/submission/<id>-'
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
        
        data["name"] = "Submission"
        
        temp["POST"] = {
                "assignment_id" : "Number",
                "submission_name" : "String",
                "submission_body" : "String",
                "submission_external_url_1" : "URL/null",
                "submission_external_url_2" : "URL/null"
            }
        temp["GET"] = None
        temp["PUT"] = {
                "assignment_id" : "Number",
                "submission_name" : "String",
                "submission_body" : "String",
                "submission_external_url_1" : "URL/null",
                "submission_external_url_2" : "URL/null"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
