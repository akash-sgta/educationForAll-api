from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response

from datetime import datetime

# ------------------------------------------------------------

from user_personal.models import (
        Diary,
        Submission,
        Notification,
        User_Notification_Int,
        Assignment_Submission_Int,
        Enroll,
    )

from user_personal.serializer import (
        Diary_Serializer,
        Submission_Serializer,
        Notification_Serializer,
        User_Notification_Int_Serializer,
        Enroll_Serializer,
    )

from auth_prime.models import (
        User_Credential
    )

from content_delivery.models import (
        Post,
        Coordinator,
        Subject,
        Assignment,
        Subject_Coordinator_Int
    )

from auth_prime.important_modules import (
        am_I_Authorized
    )

# -----------------------DIARY-------------------------------------

@csrf_exempt
def api_diary_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            diary_serialized = Diary_Serializer(data=request.data)
            diary_serialized.initial_data['user_credential_id'] = int(auth[1])
            if(diary_serialized.is_valid()):
                diary_serialized.save()
                data['success'] = True
                data['data'] = diary_serialized.data
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = f"error:SERIALIZING_ERROR, message:{diary_serialized.errors}"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                if(int(pk) == 0):
                    diary_ref = Diary.objects.filter(user_credential_id = auth[1])
                    diary_serialized = Diary_Serializer(diary_ref, many=True)
                else:
                    diary_ref = Diary.objects.get(user_credential_id = auth[1], diary_id=pk)
                    diary_serialized = Diary_Serializer(diary_ref, many=False)
            except Diary.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                data['success'] = True
                data['data'] = diary_serialized.data
                return Response(data=data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                diary_ref = Diary.objects.get(user_credential_id = auth[1], diary_id = pk)
            except Diary.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
            else:
                diary_serialized = Diary_Serializer(diary_ref, data=request.data)
                diary_serialized.initial_data['user_credential_id'] = auth[1]
                # diary_serialized.initial_data['p']
                if(diary_serialized.is_valid()):
                    diary_serialized.save()
                    data['success'] = True
                    data['data'] = diary_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = f"error:SERIALIZING_ERROR, message:{diary_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                diary_ref = Diary.objects.get(user_credential_id = auth[1], diary_id = pk)
            except Diary.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
            else:
                diary_ref.delete()
                data['success'] = True
                data['message'] = "DIARY deleted"
                return Response(data = data, status=status.HTTP_202_ACCEPTED)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/diary/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/diary/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/diary/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/personal/diary/create/",
                        "read":"api/personal/diary/read/<id>",
                        "edit":"api/personal/diary/edit/<id>",
                        "delete":"api/personal/diary/delete/<id>",
                    }, safe=True)

# -----------------------SUBMISISON-------------------------------------

@csrf_exempt
def api_submission_view(request, job, pk=None, pkk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            submission_serialized = Submission_Serializer(data = request.data)
            submission_serialized.initial_data['user_credential_id'] = int(auth[1])
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
                    data['message'] = f"error:SERIALIZING_ERROR, message:{submission_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, pkk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                # /pk/pkk
                # pk - 0, pkk - None    ->  User demanding all their submission
                # pk - 0, pkk - x       ->  Coordiantor demanding all submission under assignment [x]
                # pk - x, pkk - None    ->  User demanding for submission [x]
                if(int(pk) == 0):
                    if(pkk not in (None, "")): # Coordiantor demanding all submission under assignment [x]
                        coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
                        if(len(coordinator_ref) < 1):
                            data['success'] = False
                            data['message'] = "USER not COORDINATOR"
                            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            many_to_many_ref = Assignment_Submission_Int.objects.filter(assignment_id = int(pkk))
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
                    else:
                        submission_ref = Submission.objects.filter(user_credential_id = auth[1])
                        submission_serialized = Submission_Serializer(submission_ref, many=True).data
                        temp = list()
                        for subS in submission_serialized:
                            intermediate = Assignment_Submission_Int.objects.get(submission_id = subS['submission_id'])
                            temp.append({
                                "assignment_id" : None if(intermediate.assignment_id == None) else intermediate.assignment_id.assignment_id,
                                "submission" : subS,
                                "marks" : intermediate.marks
                            })
                        data['success'] = True
                        data['data'] = temp.copy()
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:
                    try:
                        submission_ref = Submission.objects.get(user_credential_id = auth[1], submission_id=int(pk))
                    except Submission.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist or does not belong to user"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        submission_serialized = Submission_Serializer(submission_ref, many=False).data
                        intermediate = Assignment_Submission_Int.objects.get(submission_id = submission_serialized['submission_id'])
                        data['success'] = True
                        data['data'] = {
                            "assignment_id" : None if(intermediate.assignment_id == None) else intermediate.assignment_id.assignment_id,
                            "submission" : submission_serialized,
                            "marks" : intermediate.marks
                        }
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
            except Exception as ex:
                print("EX : ", ex)
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                submission_ref = Submission.objects.get(user_credential_id = auth[1], submission_id = pk)
            except Submission.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                submission_serialized = Submission_Serializer(submission_ref, data=request.data)
                submission_serialized.initial_data['user_credential_id'] = int(user_id)
                submission_serialized.initial_data['assignment_id'] = submission_ref.assignment_id.assignment_id
                if(submission_serialized.is_valid()):
                    submission_serialized.save()
                    data['success'] = True
                    data['data'] = submission_serialized.data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    data['success'] = False
                    data['message'] = f"error:SERIALIZING_ERROR, message:{submission_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                submission_ref = Submission.objects.get(user_credential_id = auth[1], submission_id = pk)                    
            except Submission.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                submission_ref.delete()
                data['success'] = True
                data['message'] = "SUBMISSION deleted"
                return Response(data = data)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/submission/read/<id>/<id>"}, safe=True)
            else:
                return read(request, pk, pkk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/submission/edit/<id>/"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/submission/delete/<id>/"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/personal/submission/create//",
                        "read":"api/personal/submission/read/<id>/<id>",
                        "edit":"api/personal/submission/edit/<id>/",
                        "delete":"api/personal/submission/delete/<id>/",
                    }, safe=True)

# ----------------------NOTIFICATION--------------------------------------

@csrf_exempt
def api_notification_view(request, job, pk=None, pkk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            submission_serialized = Submission_Serializer(data = request.data)
            submission_serialized.initial_data['user_credential_id'] = int(auth[1])
            if(submission_serialized.is_valid()):
                submission_serialized.save()
                data['success'] = True
                data['data'] = submission_serialized.data
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = f"error:SERIALIZING_ERROR, message:{submission_serialized.errors}"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, pkk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                # /pk/pkk
                # pk - 0, pkk - None    ->  User demanding all their submission
                # pk - 0, pkk - x       ->  Coordiantor demanding all submission under assignment [x]
                # pk - x, pkk - None    ->  User demanding for submission [x]
                if(int(pk) == 0):
                    if(pkk not in (None, "")):
                        coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
                        if(len(coordinator_ref) < 1):
                            data['success'] = False
                            data['message'] = "USER not COORDINATOR"
                            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            submission_ref = Submission.objects.filter(assignment_id = int(pkk))
                            submission_serialized = Submission_Serializer(submission_ref, many=True)
                            data['success'] = True
                            data['data'] = submission_serialized.data
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:
                        submission_ref = Submission.objects.filter(user_credential_id = auth[1])
                        submission_serialized = Submission_Serializer(submission_ref, many=True)
                        data['success'] = True
                        data['data'] = submission_serialized.data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:
                    try:
                        submission_ref = Submission.objects.get(user_credential_id = auth[1], submission_id=int(pk))
                    except Submission.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist or does not belong to user"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        submission_serialized = Submission_Serializer(submission_ref, many=False)
                        data['success'] = True
                        data['data'] = submission_serialized.data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
            except Exception as ex:
                print("EX : ", ex)
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                submission_ref = Submission.objects.get(user_credential_id = auth[1], submission_id = pk)
            except Submission.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                submission_serialized = Submission_Serializer(submission_ref, data=request.data)
                submission_serialized.initial_data['user_credential_id'] = int(user_id)
                submission_serialized.initial_data['assignment_id'] = submission_ref.assignment_id.assignment_id
                if(submission_serialized.is_valid()):
                    submission_serialized.save()
                    data['success'] = True
                    data['data'] = submission_serialized.data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    data['success'] = False
                    data['message'] = f"error:SERIALIZING_ERROR, message:{submission_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                submission_ref = Submission.objects.get(user_credential_id = auth[1], submission_id = pk)                    
            except Submission.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                submission_ref.delete()
                data['success'] = True
                data['message'] = "SUBMISSION deleted"
                return Response(data = data)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/notification/read/<id>"}, safe=True)
            else:
                return read(request, pk, pkk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/notification/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/notification/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/personal/notification/create/",
                        "read":"api/personal/notification/read/<id>",
                        "edit":"api/personal/notification/edit/<id>",
                        "delete":"api/personal/notification/delete/<id>",
                    }, safe=True)

# ----------------------ENROLL--------------------------------------

@csrf_exempt
def api_enroll_view(request, job, pk=None, pkk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                enroll_ref = Enroll.objects.get(user_credential_id = auth[1], subject_id = request.data['subject_id'])
            except Enroll.DoesNotExist:
                enroll_serialized = Enroll_Serializer(data = request.data)
                enroll_serialized.initial_data['user_credential_id'] = int(auth[1])
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

    @api_view(['GET', ])
    def read(request, pk, pkk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                # coordinator   -   0   -   All enrollment under thier subject
                # others        -   0   -   All subjects enrolled
                if(int(pk) == 0):
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
                    if(len(coordinator_ref) < 1): # normal user
                        data['success'] = True
                        subject_list = list()
                        for one in Enroll_Serializer(Enroll.objects.filter(user_credential_id = auth[1]), many=True).data:
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

    # @api_view(['PUT', ])
    '''
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                submission_ref = Submission.objects.get(user_credential_id = auth[1], submission_id = pk)
            except Submission.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                submission_serialized = Submission_Serializer(submission_ref, data=request.data)
                submission_serialized.initial_data['user_credential_id'] = int(user_id)
                submission_serialized.initial_data['assignment_id'] = submission_ref.assignment_id.assignment_id
                if(submission_serialized.is_valid()):
                    submission_serialized.save()
                    data['success'] = True
                    data['data'] = submission_serialized.data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    data['success'] = False
                    data['message'] = f"error:SERIALIZING_ERROR, message:{submission_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    '''

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            try:
                enroll_ref = Enroll.objects.get(user_credential_id = auth[1], subject_id = pk)
            except Enroll.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                enroll_ref.delete()
                data['success'] = True
                data['message'] = "ENROLLMENT deleted"
                return Response(data = data, status=status.HTTP_202_ACCEPTED)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/enroll/read/<id>"}, safe=True)
            else:
                return read(request, pk, pkk, data)
        # elif(job == 'edit'):
        #     if(pk in (None, '')):
        #         return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/enroll/edit/<id>"}, safe=True)
        #     else:
        #         return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/enroll/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/personal/enroll/create/",
                        "read":"api/personal/enroll/read/0",
                        # "edit":"api/personal/enroll/edit/<id>",
                        "delete":"api/personal/enroll/delete/<id>",
                    }, safe=True)

# ------------------------------------------------------------
