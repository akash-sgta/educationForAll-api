from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http.response import JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response

import re
import json
import os
from overrides import overrides
from datetime import datetime, timedelta
from hashlib import sha256
import string
import random

# --------------------------------------------------------------------------

from auth_prime.models import (
        User_Credential,
        User_Profile,
        Admin_Credential,
        Admin_Privilege,
        Admin_Cred_Admin_Prev_Int,
        User_Token_Table,
        Api_Token_Table,
        Image
    )

from auth_prime.serializer import (
        User_Credential_Serializer,
        User_Profile_Serializer,
        Admin_Privilege_Serializer,
        Admin_Credential_Serializer,
        Image_Serializer
    )

from auth_prime.authorize import Authorize
from auth_prime.authorize import Cookie

from auth_prime.important_modules import (
        am_I_Authorized,
        create_password_hashed,
        random_generator,
        create_token
    )

# ------------------------------------------------------------

# -------------------------USER_CREDENTIAL-----------------------------------

@csrf_exempt
def api_user_cred_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        
        if(request.data['action'].lower() == 'signin'):
            if(auth[0]):
                user_cred_ref = User_Credential.objects.get(user_credential_id = auth[1])
                user_cred_serialized = User_Credential_Serializer(user_cred_ref, many=False)
                data['success'] = True
                data['message'] = "User already logged in, logout first"
                return Response(data = data, status=status.HTTP_201_CREATED)
            else:
                myData = request.data['data']
                user_cred_ref = User_Credential.objects.filter(user_email = myData['email'].lower())
                if(len(user_cred_ref) < 1):
                    data['success'] = False
                    data['message'] = "Email not registered"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    user_cred_ref = user_cred_ref[0]
                    # print(f"::{user_cred_ref.user_password}")
                    # print(f"::{create_password_hashed(myData['password'])}")
                    if(user_cred_ref.user_password != create_password_hashed(myData['password'])):
                        data['success'] = False
                        data['message'] = "Password incorrect"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        data['success'] = True
                        data['data'] = create_token(user_cred_ref)
                        return Response(data = data, status=status.HTTP_201_CREATED)
        
        elif(request.data['action'].lower() == 'signup'):
            if(auth[0]):
                data['success'] = False
                data['message'] = "User already logged in, logout first"
                return Response(data = data, status=status.HTTP_403_FORBIDDEN)
            else:
                user_cred_de_serialized = User_Credential_Serializer(data = request.data['data'])
                user_cred_de_serialized.initial_data['user_email'] = user_cred_de_serialized.initial_data['user_email'].lower()
                if(len(User_Credential.objects.filter(user_email = user_cred_de_serialized.initial_data['user_email'])) > 0):
                    data['success'] = False
                    data['message'] = "Email already in use"
                    return Response(data = data, status = status.HTTP_403_FORBIDDEN)
                else:
                    user_cred_de_serialized.initial_data['user_password'] = create_password_hashed(user_cred_de_serialized.initial_data['user_password'])
                    # print(f"::{user_cred_de_serialized.initial_data['user_password']}")
                    if(user_cred_de_serialized.is_valid()):
                        user_cred_de_serialized.save()
                        data['success'] = True
                        user_cred_ref = User_Credential.objects.get(user_credential_id = user_cred_de_serialized.data['user_credential_id'])
                        data['data'] = create_token(user_cred_ref)
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = user_cred_de_serialized.errors
                        return Response(data = data, status = status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def signout(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                if(int(pk) == 0 or int(pk) == user_id): #self
                    user_token_ref = User_Token_Table.objects.filter(user_credential_id = user_id)
                    if(len(user_token_ref) < 1):
                        data['success'] = True
                        data['message'] = "User already logged out"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        user_token_ref[0].delete()
                        data['success'] = True
                        data['message'] = "User logged out"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    if(am_I_Authorized(request, 'ADMIN') > 0):
                        if(int(pk) == 666):
                            User_Token_Table.objects.all().exclude(user_credential_id = user_id).delete()
                            data['success'] = True
                            data['message'] = "All User(s) logged out"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            try:
                                user_table_ref = User_Token_Table.objects.get(user_credential_id = pk)
                            except User_Credential.DoesNotExist:
                                data['success'] = False
                                data['message'] = "item invalid"
                                return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                            else:
                                user_table_ref.delete()
                                data['success'] = True
                                data['message'] = "User logged out by ADMIN"
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "User does not have ADMIN privileges"
                        return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
            except Exception as ex:
                print("EX : ", ex)
                return Response(status = status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                if(int(pk) == 0 or int(pk) == user_id): #self
                    user_cred_ref = User_Credential.objects.get(user_credential_id = user_id)
                    data['success'] = True
                    data['data'] = User_Credential_Serializer(user_cred_ref, many=False).data
                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    if(am_I_Authorized(request, 'ADMIN') > 0):
                        if(int(pk) == 666):
                            user_cred_ref = User_Credential.objects.all()
                            data['success'] = True
                            data['data'] = User_Credential_Serializer(user_cred_ref, many=True).data
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            try:
                                user_cred_ref = User_Credential.objects.get(user_credential_id = pk)
                            except User_Credential.DoesNotExist:
                                data['success'] = False
                                data['message'] = "item invalid"
                                return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                            else:
                                data['success'] = True
                                data['data'] = User_Credential_Serializer(user_cred_ref, many=False).data
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "User does not have ADMIN privileges"
                        return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
            except Exception as ex:
                print("EX : ", ex)
                return Response(status = status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                user_cred_ref = User_Credential.objects.filter(user_credential_id = user_id)
            except User_Credential.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                user_cred_ref = user_cred_ref[0]
                user_cred_serialized = User_Credential_Serializer(user_cred_ref, data=request.data)
                user_cred_serialized.initial_data['user_credential_id'] = int(user_id)
                user_cred_serialized.initial_data['user_email'] = user_cred_serialized.initial_data['user_email'].lower()
                test_ref = User_Credential.objects.filter(user_email = user_cred_serialized.initial_data['user_email'])
                if(len(test_ref) > 0 and test_ref[0].user_credential_id != user_id):
                    data['success'] = False
                    data['message'] = "Email already used by someone"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if(user_cred_serialized.is_valid()):
                        user_cred_serialized.save()
                        data['success'] = True
                        data['data'] = user_cred_serialized.data
                        return Response(data = data)
                    else:
                        data['success'] = False
                        data['message'] = f"error:SERIALIZING_ERROR, message:{user_cred_serialized.errors}"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                if(int(pk) == 0 or int(pk) == user_id): #self
                    User_Credential.objects.get(user_credential_id = user_id).delete()
                    data['success'] = True
                    data['message'] = "User Deleted"
                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    if(am_I_Authorized(request, 'ADMIN') > 0):
                        if(int(pk) == 666):
                            User_Credential.objects.all().exclude(user_credential_id = user_id).delete()
                            data['success'] = True
                            data['message'] = "All User(s) Deleted"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            try:
                                user_cred_ref = User_Credential.objects.get(user_credential_id = pk)
                            except User_Credential.DoesNotExist:
                                data['success'] = False
                                data['message'] = "item invalid"
                                return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                            else:
                                user_cred_ref.delete()
                                data['success'] = True
                                data['message'] = "User Deleted by ADMIN"
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "User does not have ADMIN privileges"
                        return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
            except Exception as ex:
                print("EX : ", ex)
                return Response(status = status.HTTP_400_BAD_REQUEST)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        job = job.lower()
        data = am_I_Authorized(request, "USER")
        if(job == 'create'):
            return create(request, data)
        elif(job in ('signout', 'logout')):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/cred/signout/<id>"}, safe=True)
            else:
                return signout(request, pk, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/cred/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/cred/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/cred/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/user/cred/create/",
                        "read":"api/user/cred/read/<id>",
                        "edit":"api/user/cred/edit/<id>",
                        "delete":"api/user/cred/delete/<id>",
                    }, safe=True)

# -------------------------USER_PROFILE-----------------------------------

@csrf_exempt
def api_user_prof_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            data = dict()
            user_cred_ref = User_Credential.objects.get(user_credential_id = user_id)
            if(user_cred_ref.user_profile_id in (None, "")):
                user_prof_serialized = User_Profile_Serializer(data=request.data)
                if(user_prof_serialized.initial_data['prime'] == True
                and user_prof_serialized.initial_data['user_roll_number'] in (None, "")):
                    data['success'] = False
                    data['message'] = "Student profile requires roll number"
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if(user_prof_serialized.is_valid()):
                        user_prof_serialized.save()

                        user_prof_ref = User_Profile.objects.get(user_profile_id = user_prof_serialized.data['user_profile_id'])
                        user_cred_ref.user_profile_id = user_prof_ref
                        user_cred_ref.save()
                        
                        data['success'] = True
                        data['data'] = user_prof_serialized.data
                        return Response(data=data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = f"error:SERIALIZING_ERROR, message:{user_prof_serialized.errors}"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['success'] = True
                data['message'] = "Profile already created"
                data['data'] = User_Profile_Serializer(user_cred_ref.user_profile_id, many=False).data
                return Response(data = data, status=status.HTTP_201_CREATED)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                if(int(pk) == 0 or int(pk) == user_id): #self
                    user_cred_ref = User_Credential.objects.get(user_credential_id = user_id)
                    if(user_cred_ref.user_profile_id in (None, "")):
                        data['success'] = False
                        data['message'] = "User does not have profile"
                        return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                    else:
                        data['success'] = True
                        data['data'] = User_Profile_Serializer(user_cred_ref.user_profile_id, many=False).data
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    if(am_I_Authorized(request, 'ADMIN') > 0):
                        if(int(pk) == 666):
                            user_prof_ref = User_Profile.objects.all()
                            data['success'] = True
                            data['data'] = User_Profile_Serializer(user_prof_ref, many=True).data
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            try:
                                user_cred_ref = User_Credential.objects.get(user_credential_id = pk)
                            except User_Credential.DoesNotExist:
                                data['success'] = False
                                data['message'] = "item invalid"
                                return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                            else:
                                data['success'] = True
                                data['data'] = User_Profile_Serializer(user_cred_ref.user_profile_id, many=False).data
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "User does not have ADMIN privileges"
                        return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
            except Exception as ex:
                print("EX : ", ex)
                return Response(status = status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                user_cred_ref = User_Credential.objects.filter(user_credential_id = user_id)
            except User_Credential.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                user_cred_ref = user_cred_ref[0]
                user_prof_serialized = User_Profile_Serializer(user_cred_ref.user_profile_id, data=request.data)
                if(user_prof_serialized.initial_data['prime'] == True
                and user_prof_serialized.initial_data['user_roll_number'] in (None, "")):
                    data['success'] = False
                    data['message'] = "Student profile requires roll number"
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if(user_prof_serialized.is_valid()):
                        user_prof_serialized.save()
                        data['success'] = True
                        data['data'] = user_prof_serialized.data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = f"error:SERIALIZING_ERROR, message:{user_prof_serialized.errors}"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                if(int(pk) == 0 or int(pk) == user_id): #self
                    usr = User_Credential.objects.get(user_credential_id = user_id)
                    if(usr.user_profile_id == None):
                        data['success'] = True
                        data['message'] = "User Profile Not found"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        usr.user_profile_id.delete()
                        data['success'] = True
                        data['message'] = "User Profile Deleted"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                else:
                    if(am_I_Authorized(request, 'ADMIN') > 0):
                        if(int(pk) == 666):
                            User_Profile.objects.all().delete()
                            data['success'] = True
                            data['message'] = "All User Profile(s) Deleted"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            try:
                                user_cred_ref = User_Credential.objects.get(user_credential_id = pk)
                            except User_Credential.DoesNotExist:
                                data['success'] = False
                                data['message'] = "item invalid"
                                return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                            else:
                                if(user_cred_ref.user_profile_id == None):
                                    data['success'] = True
                                    data['message'] = "User Profile Not found"
                                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                                else:
                                    usr.user_profile_id.delete()
                                    data['success'] = True
                                    data['message'] = "User Profile Deleted by ADMIN"
                                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "User does not have ADMIN privileges"
                        return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
            except Exception as ex:
                print("EX : ", ex)
                return Response(status = status.HTTP_400_BAD_REQUEST)

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
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/prof/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/prof/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/prof/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/user/prof/create/",
                        "read":"api/user/prof/read/<id>",
                        "edit":"api/user/prof/edit/<id>",
                        "delete":"api/user/prof/delete/<id>",
                    }, safe=True)

# -------------------------ADMIN_CREDENTIAL-----------------------------------

@csrf_exempt
def api_admin_cred_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(am_I_Authorized(request, "ADMIN") < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = auth[1]
                data = dict()
                id = request.data['user_id']
                try:
                    user_cred_ref = User_Credential.objects.get(user_credential_id = int(id))
                except User_Credential.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    try:
                        admin_cred_ref = Admin_Credential.objects.get(user_credential_id = id)
                    except Admin_Credential.DoesNotExist:
                        data['success'] = True
                        admin_cred_ref_new = Admin_Credential(user_credential_id = user_cred_ref).save()
                        data['data'] = Admin_Credential_Serializer(admin_cred_ref_new, many=False).data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = True
                        data['message'] = f"Admin already exists"
                        privileges = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_cred_ref.admin_credential_id)
                        priv_list = list()
                        for priv in privileges:
                            priv_list.append(priv.admin_privilege_id.admin_privilege_id)
                        data['success'] = True
                        data['data'] = {
                            "admin" : Admin_Credential_Serializer(admin_cred_ref, many=False).data,
                            "privilege" : priv_list
                        }
                        return Response(data = data, status=status.HTTP_201_CREATED)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            if(am_I_Authorized(request, "ADMIN") < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = auth[1]
                try:
                    if(int(pk) == 0 or int(pk) == user_id): #self
                        admin_cred_ref = Admin_Credential.objects.get(user_credential_id = user_id)
                        privileges = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_cred_ref.admin_credential_id)
                        priv_list = list()
                        for priv in privileges:
                            priv_list.append(priv.admin_privilege_id.admin_privilege_id)
                        data['success'] = True
                        data['data'] = {
                            "admin" : Admin_Credential_Serializer(admin_cred_ref, many=False).data,
                            "privilege" : priv_list
                        }
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        if(am_I_Authorized(request, 'ADMIN') > 0):
                            if(int(pk) == 666):
                                admin_cred_ref_all = Admin_Credential.objects.all()
                                total = list()
                                for acr in admin_cred_ref_all:
                                    privileges = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = acr.admin_credential_id)
                                    priv_list = list()
                                    for priv in privileges:
                                        priv_list.append(priv.admin_privilege_id.admin_privilege_id)
                                    total.append({
                                        "admin" : Admin_Credential_Serializer(acr, many=False).data,
                                        "privilege" : priv_list.copy()
                                    })
                                data['success'] = True
                                data['data'] = total
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                            else:
                                try:
                                    admin_cred_ref = Admin_Credential.objects.get(user_credential_id = pk)
                                except Admin_Credential.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = "item User does not have ADMIN Privilege"
                                    return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                                else:
                                    privileges = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_cred_ref.admin_credential_id)
                                    priv_list = list()
                                    for priv in privileges:
                                        priv_list.append(priv.admin_privilege_id.admin_privilege_id)
                                    data['success'] = True
                                    data['data'] = {
                                            "admin" : Admin_Credential_Serializer(admin_cred_ref, many=False).data,
                                            "privilege" : priv_list.copy()
                                        }
                                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = "User does not have ADMIN privileges"
                            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status = status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            if(am_I_Authorized(request, "ADMIN") < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                privilege = int(request.data['privilege'])
                user_id = auth[1]
                if(Admin_Credential.objects.get(user_credential_id = user_id).prime == False):
                    data['success'] = False
                    data['message'] = "Only ADMIN PRIME authorized to change PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if(int(pk) in (0, user_id)): #self change
                        if(privilege  > 0):
                            many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(
                                                admin_credential_id = Admin_Credential.objects.get(user_credential_id = user_id),
                                                admin_privilege_id = privilege
                                            )
                            if(len(many_to_many) > 0):
                                data['success'] = True
                                data['message'] = "SELF : ADMIN already has the PRIVILEGE"
                                return Response(data = data, status=status.HTTP_201_CREATED)
                            else:
                                privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = privilege)
                                if(len(privilege_ref) < 1):
                                    data['success'] = False
                                    data['message'] = "SELF :PRIVILEGE id invalid"
                                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    privilege_ref = privilege_ref[0]
                                    Admin_Cred_Admin_Prev_Int(
                                        admin_credential_id = Admin_Credential.objects.get(user_credential_id = user_id),
                                        admin_privilege_id = privilege_ref
                                    ).save()
                                    data['success'] = True
                                    data['message'] = "SELF : PRIVILEGE granted to ADMIN"
                                    return Response(data = data, status=status.HTTP_201_CREATED)
                        else:
                            privilege = privilege*-1
                            many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(
                                                admin_credential_id = Admin_Credential.objects.get(user_credential_id = user_id),
                                                admin_privilege_id = privilege
                                            )
                            if(len(many_to_many) < 1):
                                data['success'] = True
                                data['message'] = "SELF : ADMIN does not the PRIVILEGE"
                                return Response(data = data, status=status.HTTP_202_ACCEPTED)
                            else:
                                many_to_many[0].delete()
                                data['success'] = True
                                data['message'] = "SELF : PRIVILEGE revoked from ADMIN"
                                return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    else:
                        if(privilege  > 0):
                            many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(
                                                admin_credential_id = Admin_Credential.objects.get(user_credential_id = int(pk)),
                                                admin_privilege_id = privilege
                                            )
                            if(len(many_to_many) > 0):
                                data['success'] = True
                                data['message'] = "ADMIN already has the PRIVILEGE"
                                return Response(data = data, status=status.HTTP_201_CREATED)
                            else:
                                privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = privilege)
                                if(len(privilege_ref) < 1):
                                    data['success'] = False
                                    data['message'] = "PRIVILEGE id invalid"
                                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    privilege_ref = privilege_ref[0]
                                    Admin_Cred_Admin_Prev_Int(
                                        admin_credential_id = Admin_Credential.objects.get(user_credential_id = int(pk)),
                                        admin_privilege_id = privilege_ref
                                    ).save()
                                    data['success'] = True
                                    data['message'] = "PRIVILEGE granted to ADMIN"
                                    return Response(data = data, status=status.HTTP_201_CREATED)
                        else:
                            privilege = privilege*-1
                            many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(
                                                admin_credential_id = Admin_Credential.objects.get(user_credential_id = int(pk)),
                                                admin_privilege_id = privilege
                                            )
                            if(len(many_to_many) < 1):
                                data['success'] = True
                                data['message'] = "ADMIN does not the PRIVILEGE"
                                return Response(data = data, status=status.HTTP_202_ACCEPTED)
                            else:
                                many_to_many[0].delete()
                                data['success'] = True
                                data['message'] = "PRIVILEGE revoked from ADMIN"
                                return Response(data = data, status=status.HTTP_202_ACCEPTED)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            if(am_I_Authorized(request, "ADMIN") < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = auth[1]
                try:
                    if(int(pk) == 0 or int(pk) == user_id): #self
                        Admin_Credential.objects.get(user_credential_id = user_id).delete()
                        data['success'] = True
                        data['message'] = "Admin Profile deleted"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        if(am_I_Authorized(request, 'ADMIN') > 0):
                            if(int(pk) == 666):
                                Admin_Credential.objects.all().exclude(user_credential_id = user_id).delete()
                                data['success'] = True
                                data['message'] = "All Admin Profile(s) Deleted"
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                            else:
                                try:
                                   admin_cred_ref = Admin_Credential.objects.get(user_credential_id = pk)
                                except Admin_Credential.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = "item invalid"
                                    return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                                else:
                                    admin_cred_ref.delete()
                                    data['success'] = True
                                    data['message'] = "Admin Profile deleted"
                                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = "User does not have ADMIN privileges"
                            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status = status.HTTP_400_BAD_REQUEST)

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
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/admin/cred/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/admin/cred/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/admin/cred/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/admin/prev/create/",
                        "read":"api/admin/prev/read/<id>",
                        "edit":"api/admin/prev/edit/<id>",
                        "delete":"api/admin/prev/delete/<id>",
                    }, safe=True)

# -------------------------ADMIN_PRIVILEGE-----------------------------------

@csrf_exempt
def api_admin_priv_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(am_I_Authorized(request, "ADMIN") < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = auth[1]
                data = dict()
                description = " ".join(word.capitalize() for word in request.data['admin_privilege_description'].split())
                admin_prev_ref = Admin_Privilege.objects.filter(
                                    admin_privilege_name = request.data['admin_privilege_name'].upper(),
                                    admin_privilege_description = description
                                )
                if(len(admin_prev_ref) > 0):
                    data['success'] = True
                    data['message'] = "PRIVILEGE already exists"
                    data['data'] = Admin_Privilege_Serializer(admin_prev_ref[0], many=False).data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    description = " ".join(word.capitalize() for word in request.data['admin_privilege_description'].split())
                    admin_prev_ref_new = Admin_Privilege(
                                        admin_privilege_name = request.data['admin_privilege_name'].upper(),
                                        admin_privilege_description = description
                                    )
                    admin_prev_ref_new.save()
                    data['success'] = True
                    data['data'] = Admin_Privilege_Serializer(admin_prev_ref_new, many=False).data
                    return Response(data = data, status=status.HTTP_201_CREATED)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            if(am_I_Authorized(request, "ADMIN") < 1):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = auth[1]
                try:
                    if(int(pk) == 0): #all
                        data['success'] = True
                        data['data'] = Admin_Privilege_Serializer(Admin_Privilege.objects.all(), many=True).data
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            admin_priv_ref = Admin_Privilege.objects.get(admin_privilege_id = int(pk))
                        except Admin_Privilege.DoesNotExist:
                            data['success'] = False
                            data['message'] = "item does not exist"
                            return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                        else:
                            data['success'] = True
                            data['data'] = Admin_Privilege_Serializer(admin_priv_ref, many=False).data
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status = status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            if(am_I_Authorized(request, "ADMIN") < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = auth[1]
                try:
                    admin_priv_ref = Admin_Privilege.objects.get(admin_privilege_id = int(pk))
                except Admin_Privilege.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    admin_priv_de_serialized = Admin_Privilege_Serializer(admin_priv_ref, data = request.data)
                    if(admin_priv_de_serialized.is_valid()):
                        admin_priv_de_serialized.save()
                        data['success'] = True
                        data['data'] = admin_priv_de_serialized.data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = admin_priv_de_serialized.errors
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            if(am_I_Authorized(request, "ADMIN") < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = auth[1]
                if(int(pk) == 0):
                    Admin_Privilege.objects.all().delete()
                    data['success'] = True
                    data['message'] = "All ADMIN PRIVILEGE(s) Deleted"
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                try:
                    admin_priv = Admin_Privilege.objects.get(admin_privilege_id = int(pk))
                except Admin_Privilege.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    admin_priv.delete()
                    data['success'] = True
                    data['message'] = "ADMIN PRIVILEGE Deleted"
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
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/admin/prev/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/admin/prev/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/admin/prev/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/admin/prev/create/",
                        "read":"api/admin/prev/read/<id>",
                        "edit":"api/admin/prev/edit/<id>",
                        "delete":"api/admin/prev/delete/<id>",
                    }, safe=True)

# -------------------------USER_PROFILE_IMAGE-----------------------------------
@csrf_exempt
def api_user_prof_image_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(len(request.FILES) < 1):
                data['success'] = False
                data['message'] = "No data passed to api endpoint"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                image_file = request.FILES['image']
                if(str(image_file.content_type).startswith("image")):
                    if(image_file.size < 5000000):
                        if not os.path.exists('media/uploads/images'):
                            os.makedirs('media/uploads/images')

                        fs = FileSystemStorage('media/uploads/images')
                        file_name = fs.save(image_file.name, image_file)
                        file_url = fs.url(file_name)
                        image_ref = Image(image_url = file_url, image_name = file_name)
                        image_ref.save()
                        data['success'] = True
                        serialized = Image_Serializer(image_ref, many=False).data
                        serialized['image_url'] = "media/uploads/images/"+"/".join(serialized['image_url'].split("/")[2:])
                        data['data'] = serialized
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = "Image size should be less than 5MB"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data['success'] = False
                    data['message'] = "File shoud be image file"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            try:
                image_ref = Image.objects.get(image_id = int(pk))
            except Image.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['success'] = True
                data['data'] = "media/uploads/images/"+"/".join(image_ref.image_url.split("/")[2:])
                return Response(data = data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            if(am_I_Authorized(request, "ADMIN") < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_id = auth[1]
                # create new
                image_file = request.FILES['image']
                if(str(image_file.content_type).startswith("image")):
                    if(image_file.size < 5000000):
                        
                        # delete old
                        try:
                            image_ref = Image.objects.get(image_id = int(pk))
                        except Image.DoesNotExist:
                            data['success'] = False
                            data['message'] = "item does not exist"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            fs = FileSystemStorage('media/uploads/images')
                            if(fs.exists(image_ref.image_name)):
                                fs.delete(image_ref.image_name)
                            #cimage_ref.delete()
                        
                        # create new
                        file_name = fs.save(image_file.name, image_file)
                        file_url = fs.url(file_name)
                        image_ref.image_url = file_url
                        image_ref.image_name = file_name
                        image_ref.save()
                        data['success'] = True
                        serialized = Image_Serializer(image_ref, many=False).data
                        serialized['image_url'] = "media/uploads/images/"+"/".join(serialized['image_url'].split("/")[2:])
                        data['message'] = "New Image set"
                        data['data'] = serialized
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = "Image size should be less than 5MB"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data['success'] = False
                    data['message'] = "File shoud be image file"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            try:
                image_ref = Image.objects.get(image_id = int(pk))
            except Image.DoesNotExist:
                data['success'] = False
                data['message'] = "item does not exist"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                fs = FileSystemStorage('media/uploads/images')
                if(fs.exists(image_ref.image_name)):
                    fs.delete(image_ref.image_name)
                image_ref.delete()
                data['success'] = True
                data['data'] = "Image deleted"
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
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/image/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/image/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/user/image/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return JsonResponse({
                        "create":"api/user/image/create/",
                        "read":"api/user/image/read/<id>",
                        "edit":"api/user/image/edit/<id>",
                        "delete":"api/user/image/delete/<id>",
                    }, safe=True)

# ------------------------------------------------------------


# ------------------------------VIEW_SPACE-------------------------------------

pinned = [

    '<span style="color: yellow;">[25-02-2021]</span> All methods migrated to POST -> check postman export for clarity',
    '<span style="color: yellow;">[23-02-2021]</span> FETCH method have been changed to REQUEST method',

]

def api_token_web(request, word=None):
    auth = Authorize()
    cookie = Cookie()
    data_returned = dict()

    data_returned['site_name'] = 'API'

    if(request.method == 'GET'):
        if(word != None):
            if(word.upper() == 'signin'.upper()):
                type = 'signin'.upper()
            else:
                auth.clear()
                type = 'logged'.upper()
        else:
            type = 'signup'.upper()
        
        data = cookie.check_authentication_info(request)
        if(data[0] == True):
            type = 'logged'.upper()
            api_ref = Api_Token_Table.objects.get(pk = data[1])
            data_returned['user'] = api_ref
            data_returned['type'] = 'logged'.upper()
            data_returned['pinned'] = pinned
            return render(request, 'auth_prime/api.html', data_returned)
            # return cookie.set_authentication_info(request=request, file_path='auth_prime/api.html', data=data_returned, pk=api_ref.pk)
        
        data_returned['type'] = type

        return render(request, 'auth_prime/api.html', data_returned)
    
    elif(request.method == 'POST'):
        temp = dict(request.POST)
        if(temp['form_type'][0] == 'signup'):
            keys = ('user_f_name', 'user_l_name', 'user_email', 'user_password', 'api_endpoint')
            
            auth.clear()
            try:
                auth.user_password = f"{temp[keys[3]][0]}"
                data = auth.create_password_hashed()
            except Exception as ex:
                messages.add_message(request, messages.INFO, str(ex))
                data_returned['type'] = 'signup'.upper()
                return render(request, 'auth_prime/api.html', data_returned)
            else:
                if(data[0] == False):
                    print("------------------------------------------------------------------")
                    print(f"[.] API TOKEN GENERATION : UNSUCCESSFUL : HASHING ERROR.")
                else:
                    try:
                        api_new = Api_Token_Table(user_name = f"{temp[keys[0]][0]} {temp[keys[1]][0]}",
                                                  user_email = f"{temp[keys[2]][0].lower()}",
                                                  user_password = f"{data[1]}",
                                                  user_key_private = auth.random_generator(),
                                                  api_endpoint = temp[keys[4]][0])
                        api_new.save()
                    except Exception as ex:
                        print("------------------------------------------------------------------")
                        print(f"[.] API TOKEN GENERATION : UNSUCCESSFUL")
                        print(f"[x] Exception : {str(ex)}")
                    else:
                        print("------------------------------------------------------------------")
                        print(f"[.] API TOKEN GENERATION : SUCCESSFUL")
                        return redirect('API_TOKEN', word='signin')
        
        elif(temp['form_type'][0] == 'signin'):
            keys = ['user_email', 'user_password']

            auth.clear()
            try:
                auth.user_password = f"{temp[keys[1]][0]}"
                data = auth.create_password_hashed()
            except Exception as ex:
                messages.add_message(request, messages.INFO, str(ex))
                data_returned['type'] = 'signin'.upper()
                return render(request, 'auth_prime/api.html', data_returned)
            else:
                if(data[0] == False):
                    print("------------------------------------------------------------------")
                    print(f"[.] API TOKEN GENERATION : UNSUCCESSFUL : HASHING ERROR.")
                else:
                    try:
                        api_ref = Api_Token_Table.objects.filter(user_email = f"{temp[keys[0]][0].lower()}",
                                                                 user_password = data[1])
                        if(len(api_ref) < 1):
                            messages.add_message(request, messages.INFO, "Wrong Credentials ! Try again !")
                            data_returned['type'] = 'signin'.upper()
                            return render(request, 'auth_prime/api.html', data_returned)
                        else:
                            api_ref = api_ref[0]
                            data_returned['user'] = api_ref
                            data_returned['type'] = 'logged'.upper()
                            data_returned['pinned'] = pinned
                            return cookie.set_authentication_info(request=request, file_path='auth_prime/api.html', data=data_returned, pk=api_ref.pk)
                    except Exception as ex:
                        print(f"[x] API KEY LOGIN : {str(ex)}")
            
            return render(request, 'auth_prime/api.html', data_returned)
        
        elif(temp['form_type'][0] == 'signout'):

            data_returned['type'] = 'signin'.upper()
            return cookie.revoke_authentication_info(request, 'auth_prime/api.html', data_returned)
        
        else:
            return redirect('AUTH_TOKEN')

        