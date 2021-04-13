from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response

from datetime import datetime

#------------------------------------------------------------------

from auth_prime.models import (
        User_Credential,
        Api_Token_Table
    )

from auth_prime.serializer import (
        Api_Token_Serializer
    )

from analytics.models import (
        Ticket,
        Log
    )

from analytics.serializer import (
        Ticket_Serializer,
        Log_Serializer
    )

from auth_prime.important_modules import (
        am_I_Authorized,
        do_I_Have_Privilege
    )

#------------------------------------------------------------------

# -----------------------ASSIGNMENT-------------------------------

@csrf_exempt
def api_ticket_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            ticket_de_serialized = Ticket_Serializer(data = request.data)
            ticket_de_serialized.initial_data['user_credential_id'] = auth[1]
            if(ticket_de_serialized.is_valid()):
                ticket_de_serialized.save()
                data['success'] = True
                data['data'] = ticket_de_serialized.data
                return Response(data = data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = ticket_de_serialized.errors
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # pk    -   0   -   all
            # pk    -   1   -   unsolved
            # pk    -   2   -   solved
            user_id = auth[1]
            if(am_I_Authorized(request, "admin") > 0):
                pk = int(pk)
                if(pk == 0):
                    data['success'] = True
                    data['data'] = Ticket_Serializer(Ticket.objects.all(), many=True).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                elif(pk == 1):
                    data['success'] = True
                    data['data'] = Ticket_Serializer(Ticket.objects.filter(prime=False), many=True).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                elif(pk == 2):
                    data['success'] = True
                    data['data'] = Ticket_Serializer(Ticket.objects.filter(prime=True), many=True).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    data['success'] = False
                    data['message'] = "item is invalid, only 0 1 2 allowed"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['success'] = False
                data['message'] = "ADMIN_NOT_AUTHORIZED"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)

    '''
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
            if(am_I_Authorized(request, "admin") > 0):
                pk = int(pk)
                if(pk == 0):
                    Ticket.objects.all().delete()
                    data['success'] = True
                    data['message'] = "All TICKET(s) deleted"
                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    try:
                        ticket_ref = Ticket.objects.get(ticket_id = pk)
                    except Ticket.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        ticket_ref.delete()
                        data['success'] = True
                        data['data'] = "TICKET deleted"
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
            else:
                data['success'] = False
                data['message'] = "ADMIN_NOT_AUTHORIZED"
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
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/analytics/ticket/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        # elif(job == 'edit'):
        #     if(pk in (None, '')):
        #         return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/analytics/ticket/edit/<id>"}, safe=True)
        #     else:
        #         return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/analytics/ticket/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/analytics/ticket/create/",
                        "read":"api/analytics/ticket/read/<id>",
                        # "edit":"api/analytics/ticket/edit/<id>",
                        "delete":"api/analytics/ticket/delete/<id>",
                    }, safe=True)

# -----------------------ASSIGNMENT-------------------------------

@csrf_exempt
def api_log_view(request, job, date=None):

    '''
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
    '''

    @api_view(['GET', ])
    def read(request, date, api, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user_id = auth[1]
            data['success'] = True
            date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d').split()[0]
            print(date)
            data['date'] = Log_Serializer(Log.objects.filter(made_date__startswith=date, api_token_id=api), many=True).data
            return Response(data = data, status=status.HTTP_202_ACCEPTED)

    '''
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
    '''

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
    '''

    # active point
    api = am_I_Authorized(request, "API")
    if(api[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : api[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        job = job.lower()
        if(job == 'read'):
            if(date in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/analytics/log/read/dd-MM-yyyy"}, safe=True)
            else:
                return read(request, date, api[1], data)
        else:
            return JsonResponse({
                        # "create":"api/content/assignment/create/",
                        "read":"api/analytics/log/read/dd-MM-yyyy",
                        # "edit":"api/content/assignment/edit/<id>",
                        # "delete":"api/content/assignment/delete/<id>",
                    }, safe=True)
        '''
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/analytics/log/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/analytics/log/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/analytics/log/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/content/assignment/create/",
                        "read":"api/content/assignment/read/<id>",
                        "edit":"api/content/assignment/edit/<id>",
                        "delete":"api/content/assignment/delete/<id>",
                    }, safe=True)
        '''

# ----------------------------------------------------------------
