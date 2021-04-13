from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.parsers import JSONParser
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
        Lecture,
        Assignment,
        Post
    )

from content_delivery.serializer import (
        Coordinator_Serializer,
        Subject_Serializer,
        Forum_Serializer,
        Reply_Serializer,
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
        Submission
    )

from user_personal.serializer import (
        Notification_Serializer,
        User_Notification_Int_Serializer,
        Enroll_Serializer,
        Submission_Serializer
    )

from auth_prime.important_modules import (
        am_I_Authorized,
        do_I_Have_Privilege
    )

host = 'localhost'

# ---------------------COORDINATOR---------------------------------

@csrf_exempt
def api_coordinator_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(am_I_Authorized(request, "ADMIN") < 2):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(do_I_Have_Privilege(request, "CAGP")):
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
                else:
                    data['success'] = False
                    data['message'] = "ADMIN does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)

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
                coordinator_ref = Coordinator.objects.all()
                coor_list = list()
                for cor in coordinator_ref:
                    many_to_many = Subject_Coordinator_Int.objects.filter(coordinator_id = cor.coordinator_id)
                    subject_list = list()
                    for one in many_to_many:
                        subject_list.append(one.subject_id.subject_id)
                    coor_list.append({
                        "coordinator" : Coordinator_Serializer(cor, many=False).data,
                        "subject" : subject_list.copy()}
                    )
                data['success'] = True
                data['data'] = coor_list
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
                        "subject" : subject_list
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
            if(am_I_Authorized(request, "ADMIN") < 2):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(do_I_Have_Privilege(request, "CAGP")):
                    id = request.data['subject']
                    if(int(id) < 0):
                        subject_ref = Subject.objects.filter(subject_id = int(id*-1))
                    else:
                        subject_ref = Subject.objects.filter(subject_id = int(id))
                    if(len(subject_ref) < 1):
                        data['success'] = False
                        data['message'] = "SUBJECT id Invalid"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        try:
                            coordinator_ref = Coordinator.objects.get(coordinator_id = int(pk))
                        except Coordinator.DoesNotExist:
                            data['success'] = False
                            data['message'] = "item invalid"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            id = int(id)
                            if(id < 0):
                                id = id*-1
                                try:
                                    many_to_many = Subject_Coordinator_Int.objects.get(
                                                        subject_id = id,
                                                        coordinator_id = int(pk)
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
                            else:
                                try:
                                    Subject_Coordinator_Int.objects.get(subject_id = id,coordinator_id = int(pk))
                                except Subject_Coordinator_Int.DoesNotExist:
                                    many_to_many = Subject_Coordinator_Int(
                                                        subject_id = subject_ref[0],
                                                        coordinator_id = coordinator_ref
                                                    )
                                    many_to_many.save()
                                    data['success'] = True
                                    data['message'] = "SUBJECT added to COORDINATOR"
                                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                else:
                                    data['success'] = True
                                    data['message'] = "SUBJECT already belong to COORDINATOR"
                                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    data['success'] = False
                    data['message'] = "ADMIN does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            if(am_I_Authorized(request, "ADMIN") < 2):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                
                if(do_I_Have_Privilege(request, "CAGP")):
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
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/coordinator/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/coordinator/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/coordinator/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/coordinator/create/",
                        "read":"api/content/coordinator/read/<id>",
                        "edit":"api/content/coordinator/edit/<id>",
                        "delete":"api/content/coordinator/delete/<id>",
                    }, safe=True)

# ------------------------SUBJECT------------------------------

@csrf_exempt
def api_subject_view(request, job, pk=None):

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
                data['data'] = Subject_Serializer(Subject.objects.all(), many=True).data
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
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/subject/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/subject/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/subject/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/subject/create/",
                        "read":"api/content/subject/read/<id>",
                        "edit":"api/content/subject/edit/<id>",
                        "delete":"api/content/subject/delete/<id>",
                    }, safe=True)

# -----------------------FORUM-------------------------------

@csrf_exempt
def api_forum_view(request, job, pk=None):

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
                forum_de_serialized = Forum_Serializer(data = request.data)
                if(forum_de_serialized.is_valid()):
                    forum_de_serialized.save()
                    data['success'] = True
                    data['data'] = forum_de_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = forum_de_serialized.errors
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
                data['data'] = Forum_Serializer(Forum.objects.all(), many=True).data
                return Response(data = data, status=status.HTTP_202_ACCEPTED)
            else:
                try:
                    forum_ref = Forum.objects.get(forum_id = int(pk))
                except Forum.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data['success'] = True
                    replies = Reply.objects.filter(forum_id = int(pk))
                    reply_list = list()
                    for reply in replies:
                        reply_list.append(reply.reply_id)
                    data['data'] = {
                                        "forum" : Forum_Serializer(forum_ref, many=False).data,
                                        "reply" : reply_list.copy()
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
                    forum_ref = Forum.objects.get(forum_id = int(pk))
                except Forum.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    forum_de_serialized = Forum_Serializer(forum_ref, data=request.data)
                    if(forum_de_serialized.is_valid()):
                        forum_de_serialized.save()
                        data['success'] = True
                        data['data'] = forum_de_serialized.data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = forum_de_serialized.errors
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
                    Forum.objects.all().delete()
                    data['success'] = True
                    data['message'] = "All FORUM(s) deleted"
                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    try:
                        forum_ref = Forum.objects.get(forum_id = int(pk))
                    except Forum.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        forum_ref.delete()
                        data['success'] = True
                        data['message'] = "FORUM deleted"
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
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/forum/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/forum/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/content/forum/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/forum/create/",
                        "read":"api/content/forum/read/<id>",
                        "edit":"api/content/forum/edit/<id>",
                        "delete":"api/content/forum/delete/<id>",
                    }, safe=True)

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
                    for sub in Submission.objects.filter(assignment_id = ass['assignment_id']):
                        sub_list.append(sub.submission_id)
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
                    for sub in Submission.objects.filter(assignment_id = assignment_serializer['assignment_id']):
                        sub_list.append(sub.submission_id)
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

# ----------------------------------------------

# ---------------------------------------------VIEW SPACE-------------------------------------------------------
