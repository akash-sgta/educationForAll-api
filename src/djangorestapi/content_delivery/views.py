from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response

from datetime import datetime

# ------------------------------------------------------

from content_delivery.models import (
        Coordinator,
        Subject,
        Subject_Coordinator_Int,
        Forum,
        Reply,
        ReplyToReply,
        Lecture,
        Assignment,
        Post
    )

from content_delivery.serializer import (
        Coordinator_Serializer,
        Subject_Serializer,
        Forum_Serializer,
        Reply_Serializer,
        ReplyToReply_Serializer,
        Lecture_Serializer,
        Assignment_Serializer,
        Post_Serializer
    )

from auth_prime.models import (
        User_Credential,
        User_Profile,
        Admin_Credential,
        Admin_Cred_Admin_Prev_Int,
        Admin_Privilege
    )

from auth_prime.serializer import (
        User_Credential_Serializer,
        User_Profile_Serializer
    )

from user_personal.models import (
        Notification,
        User_Notification_Int,
        Enroll,
        Submission,
        Assignment_Submission_Int
    )

from user_personal.serializer import (
        Notification_Serializer,
        User_Notification_Int_Serializer,
        Enroll_Serializer,
        Submission_Serializer,
        Assignment_Submission_Int_Serializer
    )

from auth_prime.important_modules import (
        am_I_Authorized,
        do_I_Have_Privilege
    )

host = 'localhost'

# ---------------------COORDINATOR---------------------------------

from content_delivery.view.coordinator import Coordinator_View as cView

# ------------------------SUBJECT------------------------------

from content_delivery.view.subject import Subject_View as sView

# -----------------------FORUM-------------------------------

from content_delivery.view.forum import Forum_View as fView

# -----------------------REPLY-------------------------------

@csrf_exempt
def api_reply_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            reply_de_serialized = Reply_Serializer(data = request.data)
            reply_de_serialized.initial_data['user_credential_id'] = auth[1]
            if(reply_de_serialized.is_valid()):
                reply_de_serialized.save()
                data['success'] = True
                data['data'] = reply_de_serialized.data
                return Response(data = data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = reply_de_serialized.errors
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            if(int(pk) == 0): #all
                data['success'] = True
                data['data'] = Reply_Serializer(Reply.objects.all(), many=True).data
                return Response(data = data, status=status.HTTP_202_ACCEPTED)
            else:
                try:
                    reply_ref = Reply.objects.get(reply_id = int(pk))
                except Reply.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data['success'] = True
                    data['data'] = Reply_Serializer(reply_ref, many=False).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                reply_ref = Reply.objects.get(reply_id = int(pk), user_credential_id=auth[1])
            except Reply.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist or does not belong to user"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                reply_de_serialized = Reply_Serializer(reply_ref, data=request.data)
                if(reply_de_serialized.is_valid()):
                    reply_de_serialized.save()
                    data['success'] = True
                    data['data'] = reply_de_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = reply_de_serialized.errors
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
            if(int(pk) == 0): #all
                coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
                if(len(coordinator_ref) < 1):
                    data['success'] = False
                    data['message'] = "USER not COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    Reply.objects.all().delete()
                    data['success'] = True
                    data['message'] = "All REPL(y/ies) deleted as COORDINATOR"
                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
            else:
                try:
                    reply_ref = Reply.objects.get(reply_id = int(pk), user_credential_id = auth[1])
                except Reply.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist or does not belon to user"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    reply_ref.delete()
                    data['success'] = True
                    data['message'] = "REPLY deleted"
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        job = job.lower()
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/reply/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/reply/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/reply/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/reply/create/",
                        "read":"api/content/reply/read/<id>",
                        "edit":"api/content/reply/edit/<id>",
                        "delete":"api/content/reply/delete/<id>",
                    }, safe=True)

@csrf_exempt
def api_reply2reply_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            reply_de_serialized = ReplyToReply_Serializer(data = request.data)
            reply_de_serialized.initial_data['user_credential_id'] = auth[1]
            if(reply_de_serialized.is_valid()):
                reply_de_serialized.save()
                data['success'] = True
                data['data'] = reply_de_serialized.data
                return Response(data = data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = reply_de_serialized.errors
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            if(int(pk) == 0):
                data['success'] = False
                data['message'] = "item does not exist"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    reply_ref = ReplyToReply.objects.filter(reply_to_id = int(pk))
                except Reply.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data['success'] = True
                    data['data'] = ReplyToReply_Serializer(reply_ref, many=True).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                reply_ref = ReplyToReply.objects.get(reply_to_id = int(pk), user_credential_id=auth[1])
            except Reply.DoesNotExist:
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

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            if(int(pk) == 0): #all
                coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
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
                    reply_ref = ReplyToReply.objects.get(reply_id = int(pk), user_credential_id = auth[1])
                except ReplyToReply.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist or does not belong to user"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    reply_ref.delete()
                    data['success'] = True
                    data['message'] = "DEEP REPLY deleted"
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        job = job.lower()
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/reply2reply/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/reply2reply/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/reply2reply/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/reply2reply/create/",
                        "read":"api/content/reply2reply/read/<id>",
                        "edit":"api/content/reply2reply/edit/<id>",
                        "delete":"api/content/reply2reply/delete/<id>",
                    }, safe=True)

# -----------------------LECTURE-------------------------------

@csrf_exempt
def api_lecture_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                lecture_de_serialized = Lecture_Serializer(data = request.data)
                if(lecture_de_serialized.is_valid()):
                    lecture_de_serialized.save()
                    data['success'] = True
                    data['data'] = lecture_de_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = lecture_de_serialized.errors
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            if(int(pk) == 0): #all
                data['success'] = True
                data['data'] = Lecture_Serializer(Lecture.objects.all(), many=True).data
                return Response(data = data, status=status.HTTP_202_ACCEPTED)
            else:
                try:
                    lecture_ref = Lecture.objects.get(lecture_id = int(pk))
                except Lecture.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data['success'] = True
                    data['data'] = Lecture_Serializer(lecture_ref, many=False).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    lecture_ref = Lecture.objects.get(lecture_id = int(pk))
                except Lecture.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    lecture_de_serialized = Lecture_Serializer(lecture_ref, data=request.data)
                    if(lecture_de_serialized.is_valid()):
                        lecture_de_serialized.save()
                        data['success'] = True
                        data['data'] = lecture_de_serialized.data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = lecture_de_serialized.errors
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
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(int(pk) == 0): #all
                    Lecture.objects.all().delete()
                    data['success'] = True
                    data['message'] = "All LECTURE(s) deleted"
                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    try:
                        lecture_ref = Lecture.objects.get(lecture_id = int(pk))
                    except Lecture.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        lecture_ref.delete()
                        data['success'] = True
                        data['message'] = "LECTURE deleted"
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        job = job.lower()
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/lecture/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/lecture/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/lecture/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/lecture/create/",
                        "read":"api/content/lecture/read/<id>",
                        "edit":"api/content/lecture/edit/<id>",
                        "delete":"api/content/lecture/delete/<id>",
                    }, safe=True)

# -----------------------ASSIGNMENT-------------------------------

@csrf_exempt
def api_assignment_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
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

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            if(int(pk) == 0): #all
                data['success'] = True
                assignment_serializer = Assignment_Serializer(Assignment.objects.all(), many=True).data
                ass_list = list()
                for ass in assignment_serializer:
                    sub_list = list()
                    for one in Assignment_Submission_Int.objects.filter(assignment_id = ass['assignment_id']):
                        sub_list.append(one.submission_id.submission_id)
                    ass_list.append({
                        "assignment" : ass,
                        "submission" : sub_list.copy()
                    })
                data['data'] = ass_list.copy()
                return Response(data = data, status=status.HTTP_202_ACCEPTED)
            else:
                try:
                    assignment_ref = Assignment.objects.get(assignment_id = int(pk))
                except Assignment.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data['success'] = True
                    assignment_serializer = Assignment_Serializer(assignment_ref, many=False).data
                    sub_list = list()
                    for one in Assignment_Submission_Int.objects.filter(assignment_id = assignment_serializer['assignment_id']):
                        sub_list.append(one.subject_id.submission_id)
                    data['data'] = {
                        "assignment" : assignment_serializer,
                        "submission" : sub_list.copy()
                    }
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    assignment_ref = Assignment.objects.get(assignment_id = int(pk))
                except Assignment.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
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

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(int(pk) == 0): #all
                    Assignment.objects.all().delete()
                    data['success'] = True
                    data['message'] = "All ASSIGNMENT(s) deleted"
                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    try:
                        assignment_ref = Assignment.objects.get(assignment_id = int(pk))
                    except Assignment.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        assignment_ref.delete()
                        data['success'] = True
                        data['message'] = "ASSIGNMENT deleted"
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        job = job.lower()
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/assignment/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/assignment/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/assignment/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/assignment/create/",
                        "read":"api/content/assignment/read/<id>",
                        "edit":"api/content/assignment/edit/<id>",
                        "delete":"api/content/assignment/delete/<id>",
                    }, safe=True)

@csrf_exempt
def mark_assignment_view(request, job, pk, pkk):

    @api_view(['GET', ])
    def read(request, pk, pkk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                one_ref = Assignment_Submission_Int.objects.get(assignment_id = int(pk), submission_id = int(pkk))
            except Assignment_Submission_Int.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist"
                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            except ValueError or TypeError:
                data['success'] = False
                data['message'] = "INVALID_ID"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                one_serialized = Assignment_Submission_Int_Serializer(one_ref).data
                data['success'] = True
                data['data'] = one_serialized
                return Response(data = data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    user_data = request.data
                    user_data["assignment_id"] = pk
                    if("submission_id" not in user_data.keys() or "marks" not in user_data.keys()):
                        data['success'] = False
                        data['message'] = "KEY_VALUE_MISSING_JSON"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        one_ref = Assignment_Submission_Int.objects.get(assignment_id = int(pk), submission_id = int(user_data["submission_id"]))
                except Assignment_Submission_Int.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                except ValueError or TypeError:
                    data['success'] = False
                    data['message'] = "INVALID_DATA_JSON"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    one_serialized = Assignment_Submission_Int_Serializer(one_ref, data=user_data)
                    if(one_serialized.is_valid()):
                        one_serialized.save()
                        data['success'] = True
                        data['data'] = one_serialized.data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = one_serialized.error
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        job = job.lower()
        if(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/markAssignment/edit/<id>/"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/markAssignment/read/<id>/<idd>"}, safe=True)
            else:
                return read(request, pk, pkk, data)
        else:
            return JsonResponse({
                        "read":"api/content/assignment/read/<id>/<idd>",
                        "edit":"api/content/assignment/edit/<id>/",
                    }, safe=True)

# -----------------------POST-------------------------------

@csrf_exempt
def api_post_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                post_de_serialized = Post_Serializer(data = request.data)
                post_de_serialized.initial_data['user_credential_id'] = auth[1]
                if(post_de_serialized.is_valid()):
                    post_de_serialized.save()
                    # create notification for concerned part(y/ies)
                    # ---------------------------------------------
                    message = f"Date : {post_de_serialized.data['made_date'].split('T')[0]}"
                    message += f'''
                    \n\n<b>{Subject_Serializer(Subject.objects.get(subject_id = post_de_serialized.data['subject_id']), many=False).data['subject_name']}</b>
                    \n\n<i>{post_de_serialized.data['post_name']}</i>
                    \n{' '.join(post_de_serialized.data['post_body'].split()[:10])}...<a href="http://{host}/api/content/post/read/{post_de_serialized.data['post_id']}">[Read More]</a>
                    '''
                    try:
                        serialized = User_Credential_Serializer(User_Credential.objects.get(user_credential_id = post_de_serialized.data['user_credential_id']), many=False).data
                    except Exception as ex:
                        print("EX : ", ex)
                        message += f"\n\nCreated By : Anonymous"
                    else:
                        if(serialized['user_profile_id'] in (None, "")):
                            message += f"\n\nCreated By : {serialized['user_f_name']} {serialized['user_l_name']}"
                        else:
                            message += f'''\n\nCreated By : <a href="http://{host}/api/user/prof/read/{serialized['user_profile_id']}">{serialized['user_f_name']} {serialized['user_l_name']}</a>'''
                    notification_ref_new = Notification(
                                                post_id = Post.objects.get(post_id = post_de_serialized.data['post_id']),
                                                notification_body = message
                                            )
                    notification_ref_new.save()
                    many_to_many_enroll = Enroll.objects.filter(subject_id = post_de_serialized.data['subject_id'])
                    many_to_many_coor_sub = Subject_Coordinator_Int.objects.filter(subject_id = post_de_serialized.data['subject_id'])
                    if(len(many_to_many_coor_sub) > 0):
                        for one in many_to_many_coor_sub:
                            User_Notification_Int(
                                notification_id = notification_ref_new,
                                user_credential_id = one.coordinator_id.user_credential_id
                            ).save()
                    if(len(many_to_many_enroll) > 0):
                        for one in many_to_many_enroll:
                            User_Notification_Int(
                                notification_id = notification_ref_new,
                                user_credential_id = one.user_credential_id
                            ).save()
                    # ---------------------------------------------
                    data['success'] = True
                    data['data'] = post_de_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = post_de_serialized.errors
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            if(int(pk) == 0): #all
                temp = list()
                data['success'] = True
                data['data'] = Post_Serializer(Post.objects.all(), many=True).data
                return Response(data = data, status=status.HTTP_202_ACCEPTED)
            else:
                try:
                    post_ref = Post.objects.get(post_id = int(pk))
                except Post.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    post_ref.post_views += 1
                    post_ref.save()
                    data['success'] = True
                    data['data'] = Post_Serializer(post_ref, many=False).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    post_ref = Post.objects.get(post_id = int(pk), user_credential_id = auth[1])
                except Post.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist or does not belong to user"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    post_de_serialized = Post_Serializer(post_ref, data=request.data)
                    if(post_de_serialized.is_valid()):
                        post_de_serialized.save()
                        data['success'] = True
                        data['data'] = post_de_serialized.data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = post_de_serialized.errors
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
            coordinator_ref = Coordinator.objects.filter(user_credential_id = auth[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(int(pk) == 0): #all
                    Post.objects.all().delete()
                    data['success'] = True
                    data['message'] = "All POST(s) deleted"
                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    try:
                        post_ref = Post.objects.get(post_id = int(pk), user_credential_id = auth[1])
                    except Post.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist or does not belong to user"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        post_ref.delete()
                        data['success'] = True
                        data['message'] = "POST deleted"
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        job = job.lower()
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/post/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/post/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/post/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/post/create/",
                        "read":"api/content/post/read/<id>",
                        "edit":"api/content/post/edit/<id>",
                        "delete":"api/content/post/delete/<id>",
                    }, safe=True)

@csrf_exempt
def api_votes_view(request, word, pk=None, control=None):

    @api_view(['GET', ])
    def read(request, word, pk, control, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(word.lower() == "post"):
                try:
                    ref = Post.objects.get(post_id = int(pk))
                except Post.DoesNotExist:
                    data['success'] = False
                    data['message'] = "post does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            elif(word.lower() == "reply"):
                try:
                    ref = Reply.objects.get(reply_id = int(pk))
                except Reply.DoesNotExist:
                    data['success'] = False
                    data['message'] = "reply does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    ref = ReplyToReply.objects.get(reply_id = int(pk))
                except Post.DoesNotExist:
                    data['success'] = False
                    data['message'] = "deep reply does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
            
            if(control == '+'):
                ref.upvote += 1
                data['data'] = f"{type(ref)} : upvotes changed"
            if(control == '-'):
                ref.downvote += 1
                data['data'] = f"{type(ref)} : downvotes changed"
            ref.save()
            data['success'] = True
            return Response(data = data, status=status.HTTP_202_ACCEPTED)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        if((word.lower() not in ('post', 'reply', 'replyd')) or (pk in (None, '')) or (control not in ('+', '-'))):
            return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/votes/<post/reply/replyd>/<id>/<+/->"}, safe=True)
        else:
            return read(request, word, pk, control, data)

# ----------------------------------------------

# ---------------------------------------------VIEW SPACE-------------------------------------------------------
