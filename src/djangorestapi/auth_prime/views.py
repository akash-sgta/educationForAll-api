from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from auth_prime.models import User_Credential, Admin_Privilege, Admin_Credential, Token_Table
from auth_prime.serializer import User_Credential_Serializer, Admin_Privilege_Serializer, Admin_Credential_Serializer, Token_Table_Serializer

import json
from auth_prime.authorize import create_password_hash, is_user_authorized, is_admin_authorized, create_check_hash
# Create your views here.

@csrf_exempt
def user_API(request, id=0):
    data_returned = dict()

    if(request.method == 'FETCH'):
        data_returned['action'] = "FETCH"

        user_data = JSONParser().parse(request)
        incoming_action = user_data["action"]
        incoming_data = user_data["data"]

        if(incoming_action == 'user'):
            data_returned['action'] += '-USER'
            
            if(is_user_authorized(incoming_data['user_id'], incoming_data['hash'])
                and incoming_data['user_id'] == incoming_data['f_user_id']): # singular user info request

                users = User_Table.objects.filter(user_id=incoming_data['f_user_id'])
                if(len(users) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = 2001 # Invalid user id
                    return JsonResponse(data_returned, safe=True)
                else:
                    users = users[0]
                    data_returned['return'] = True
                    data_returned['code'] = 1000 # No error encountered
                    data_returned['data'] = dict(User_Table_Serializer(users, many=False).data)
                    return JsonResponse(data_returned, safe=True)
        
        elif(incoming_action == 'user_s'):
            data_returned['action'] += '-USER_S'

            if(is_admin_authorized(incoming_data['user_id'], incoming_data['hash'])):

                users = User_Table.objects.all()
                users_serialized = User_Table_Serializer(users, many=True)
                data_returned['return'] = True
                data_returned['code'] = 1000

                data_returned['data'] = dict()
                i = 0
                for data in users_serialized.data:
                    data_returned['data'][i] = dict(data)
                    i += 1
                
                return JsonResponse(data_returned, safe=True)

            else:
                data_returned['return'] = False
                data_returned['code'] = 3002 # unauthorized admin access
                return JsonResponse(data_returned, safe=True)
        
        else:
            data_returned['return'] = False
            data_returned['code'] = 1002 # Invalid action specified in message
            data_returned['message'] = "invalid action specified."
            return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'POST'):
        data_returned['action'] = "POST"

        user_data = JSONParser().parse(request)
        incoming_action = user_data["action"]
        incoming_data = user_data["data"]

        if(incoming_action == "signup"):

            # SIGNUP REQUEST
            # if successful return hash for login confirmation too
            
            data_returned['action'] += "-SIGNUP"

            user_de_serialized = User_Table_Serializer(data=incoming_data)
            data_to_check = user_de_serialized.initial_data
            data_to_check['user_email'] = (data_to_check['user_email']).lower()
            temp_fetch = User_Table.objects.filter(user_email=data_to_check['user_email'])

            if(len(temp_fetch) > 0):
                data_returned['return'] = False
                data_returned['code'] = 1001 # User Email Exists
                return JsonResponse(data_returned, safe=True)
            
            else:
                user_de_serialized.initial_data['user_password'] = create_password_hash(data_to_check['user_password'])

                if(user_de_serialized.is_valid()):
                    user_de_serialized.save()

                    data_returned['return'] = True
                    data_returned['code'] = 1000 # No error encountered
                    data_returned['data'] = dict()
                    data_returned['data']['user_id'] = User_Table.objects.latest('user_id').user_id
                    data_returned['data']['hash'] = create_check_hash(user_de_serialized.validated_data['user_email'],
                                                                        user_de_serialized.validated_data['user_password']) # return hash as login confirmation
                    return JsonResponse(data_returned, safe=True)
                
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 9001 # Amiguous Error
                    data_returned['message'] = user_de_serialized.errors
                    return JsonResponse(data_returned, safe=True)

        elif(incoming_action == "login"):
            data_returned['action'] += "-LOGIN"

            user_check = User_Table.objects.filter(user_email = incoming_data['user_email'].lower(),
                                    user_password = create_password_hash(incoming_data['user_password']))
            if(len(user_check) < 1):
                data_returned['return'] = False
                data_returned['code'] = 1003 # email id or password wrong
                return JsonResponse(data_returned, safe=True)
            
            else:
                user_check = user_check[0]
                data_returned['return'] = True
                data_returned['code'] = 1000 # No error encountered
                data_returned['data'] = dict()
                data_returned['data']['user_id'] = user_check.user_id
                data_returned['data']['hash'] = create_check_hash(incoming_data['user_email'].lower(),
                                                                    create_password_hash(incoming_data['user_password']))
                return JsonResponse(data_returned, safe=True)

        else:
            data_returned['return'] = False
            data_returned['code'] = 1002 # Invalid action specified in message
            data_returned['message'] = "invalid action specified."
            return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'PUT'):
        data_returned['action'] = "PUT"

        user_data = JSONParser().parse(request)
        incoming_action = user_data['action']
        incoming_data = user_data['data']

        if(incoming_action == 'user'):
            data_returned['action'] += "-USER"


            user = User_Table.objects.get(user_id = incoming_data['user_id'])

            if(incoming_data['hash'] != create_check_hash(user.user_email, user.user_password)): #hash cross validate
                data_returned['return'] = False
                data_returned['code'] = 3001
                return JsonResponse(data_returned, safe=True)
            else:
                user_de_serialized = User_Table_Serializer(user, data=incoming_data['data'])
                user_de_serialized.initial_data['user_id'] = incoming_data['user_id']

                temp = User_Table.objects.filter(user_email=user_de_serialized.initial_data['user_email'].lower())
                if(len(temp) == 1):
                    if(temp[0].user_id == user.user_id):
                        user_de_serialized.initial_data['user_email'] = user_de_serialized.initial_data['user_email'].lower()
                        user_de_serialized.initial_data['user_password'] = user.user_password
                    else:
                        data_returned['return'] = False
                        data_returned['code'] = 1001 # User Email Exists
                        return JsonResponse(data_returned, safe=True)
                else:
                    user_de_serialized.initial_data['user_email'] = user_de_serialized.initial_data['user_email'].lower()
                    user_de_serialized.initial_data['user_password'] = user.user_password

                if(user_de_serialized.is_valid()):
                    user_de_serialized.save()

                    data_returned['return'] = True
                    data_returned['code'] = 1000
                    return JsonResponse(data_returned, safe=True)
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 9001
                    data_returned['message'] = user_de_serialized.errors
                    return JsonResponse(data_returned, safe=True)
        
        else:
            data_returned['return'] = False
            data_returned['code'] = 1002 # Invalid action specified in message
            data_returned['message'] = "invalid action specified."
            return JsonResponse(data_returned, safe=True)

    elif(request.method == 'DELETE'):
        data_returned['action'] = "DELETE"

        user_data = JSONParser().parse(request)
        incoming_action = user_data['action']
        incoming_data = user_data['data']

        if(incoming_action == 'user'):
            data_returned['action'] += "-USER"

            if(is_user_authorized(incoming_data['user_id'], incoming_data['hash'])):
                user = User_Table.objects.filter(user_id=incoming_data['user_id'])

                if(len(user) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = 2001
                    return JsonResponse(data_returned, safe=True)
                else:
                    user.delete()
                    data_returned['return'] = True
                    data_returned['code'] = 1000
                    return JsonResponse(data_returned, safe=True)
            
            else:
                data_returned['return'] = False
                data_returned['code'] = 3001
                return JsonResponse(data_returned, safe=True)
        
        else:
            data_returned['return'] = False
            data_returned['code'] = 1002 # Invalid action specified in message
            data_returned['message'] = "invalid action specified."
            return JsonResponse(data_returned, safe=True)

    else:
        return JsonResponse("USER : [x] Invalid Method. read API contract.", safe=False)

@csrf_exempt
def admin_privilege_API(request, id=0):

    if(request.method == 'GET'):
        try:
            if(id == 0):
                admin_privileges = Admin_Privilege.objects.all()
                admin_privileges_serialized = Admin_Privilege_Serializer(admin_privileges, many=True)
                return JsonResponse(admin_privileges_serialized.data, safe=False)
            else:
                admin_privileges = Admin_Privilege.objects.get(privilege_id=id)
                admins_privileges_serialized = Admin_Privilege_Serializer(admin_privileges, many=False)
                return JsonResponse(admins_privileges_serialized.data, safe=False)
        except Exception as ex:
            print(f"[!] ADMIN PREV API : GET : {ex}")
            return JsonResponse("ADMIN PREV : [x] Data Get -> Unsuccessful.", safe=False)
    
    elif(request.method == 'POST'):
        admin_privilege_data = JSONParser().parse(request)
        admin_privilege_de_serialized = Admin_Privilege_Serializer(data=admin_privilege_data)
        if(admin_privilege_de_serialized.is_valid()):
            admin_privilege_de_serialized.save()
            return JsonResponse("ADMIN PREV : [.] Data Add -> Successful.", safe=False)
        else:
            return JsonResponse("ADMIN PREV : [x] Data Add -> Unsuccessful.", safe=False)
    
    elif(request.method == 'PUT'):
        admin_privilege_data = JSONParser().parse(request)
        admin_privilege = Admin_Privilege.objects.get(privilege_id = admin_privilege_data['privilege_id'])
        admin_privilege_de_serialized = Admin_Privilege_Serializer(admin_privilege, data=admin_privilege_data)
        if(admin_privilege_de_serialized.is_valid()):
            admin_privilege_de_serialized.save()
            return JsonResponse("ADMIN PREV : [.] Update -> Successful.", safe=False)
        else:
            return JsonResponse("ADMIN PREV : [x] Update -> Unsuccessful.", safe=False)
    
    elif(request.method == 'DELETE'):
        try:
            admin_privilege = Admin_Privilege.objects.get(privilege_id=id)
            admin_privilege.delete()
        except Exception as ex:
            print(f"[!] ADMIN PREV API : DELETE : {ex}")
            return JsonResponse("ADMIN PREV : [.] Delete -> Unsuccessful.", safe=False)
        else:
            return JsonResponse("ADMIN PREV : [x] Delete -> Successful.", safe=False)
    
    else:
        return JsonResponse("[x] Invalid Method. (use POST/GET/PUT/DELETE)", safe=False)

@csrf_exempt
def admin_API(request, id=0):

    if(request.method == 'GET'):
        try:
            if(id == 0):
                admins = Admin_Table.objects.all()
                admins_serialized = Admin_Table_Serializer(admins, many=True)
                return JsonResponse(admins_serialized.data, safe=False)
            else:
                admins = Admin_Table.objects.get(admin_id=id)
                admins_serialized = Admin_Table_Serializer(admins, many=False)
                return JsonResponse(admins_serialized.data, safe=False)
        except Exception as ex:
            print(f"[!] ADMIN API : GET : {ex}")
            return JsonResponse("ADMIN : [x] Data Get -> Unsuccessful.", safe=False)
    
    elif(request.method == 'POST'):
        admin_data = JSONParser().parse(request)
        admin_de_serialized = Admin_Table_Serializer(data=admin_data)
        if(admin_de_serialized.is_valid()):
            admin_de_serialized.save()
            return JsonResponse("ADMIN : [.] Data Add -> Successful.", safe=False)
        else:
            return JsonResponse("ADMIN : [x] Data Add -> Unsuccessful.", safe=False)
    
    elif(request.method == 'PUT'):
        admin_data = JSONParser().parse(request)
        admin = Admin_Table.objects.get(admin_id = admin_data['admin_id'])
        admin_de_serialized = Admin_Table_Serializer(admin, data=admin_data)
        if(admin_de_serialized.is_valid()):
            admin_de_serialized.save()
            return JsonResponse("ADMIN : [.] Update -> Successful.", safe=False)
        else:
            return JsonResponse("ADMIN : [x] Update -> Unsuccessful.", safe=False)
    
    elif(request.method == 'DELETE'):
        try:
            admin = Admin_Table.objects.get(admin_id=id)
            admin.delete()
        except Exception as ex:
            print(f"[!] ADMIN API : DELETE : {ex}")
            return JsonResponse("ADMIN : [.] Delete -> Unsuccessful.", safe=False)
        else:
            return JsonResponse("ADMIN : [x] Delete -> Successful.", safe=False)
    
    else:
        return JsonResponse("[x] Invalid Method. (use POST/GET/PUT/DELETE)", safe=False)

@csrf_exempt
def token_API(request, id=0):

    if(request.method == 'GET'):
        try:
            if(id == 0):
                tokens = Token_Table.objects.all()
                tokens_serialized = Token_Table_Serializer(tokens, many=True)
                return JsonResponse(tokens_serialized.data, safe=False)
            else:
                tokens = Token_Table.objects.get(token_id=id)
                tokens_serialized = Token_Table_Serializer(tokens, many=False)
                return JsonResponse(tokens_serialized.data, safe=False)
        except Exception as ex:
            print(f"[!] ADMIN API : GET : {ex}")
            return JsonResponse("ADMIN : [x] Data Get -> Unsuccessful.", safe=False)
    
    elif(request.method == 'POST'):
        token_data = JSONParser().parse(request)
        token_de_serialized = Token_Table_Serializer(data=token_data)
        print(token_de_serialized)
        if(token_de_serialized.is_valid()):
            token_de_serialized.save()
            return JsonResponse("TOKEN : [.] Data Add -> Successful.", safe=False)
        else:
            return JsonResponse("TOKEN : [x] Data Add -> Unsuccessful.", safe=False)
    
    elif(request.method == 'PUT'):
        token_data = JSONParser().parse(request)
        token = Token_Table.objects.get(token_id = token_data['token_id'])
        token_de_serialized = Token_Table_Serializer(token, data=token_data)
        if(token_de_serialized.is_valid()):
            token_de_serialized.save()
            return JsonResponse("TOKEN : [.] Update -> Successful.", safe=False)
        else:
            return JsonResponse("TOKEN : [x] Update -> Unsuccessful.", safe=False)
    
    elif(request.method == 'DELETE'):
        try:
            token = Token_Table.objects.get(token_id=id)
            token.delete()
        except Exception as ex:
            print(f"[!] TOKEN API : DELETE : {ex}")
            return JsonResponse("TOKEN : [.] Delete -> Unsuccessful.", safe=False)
        else:
            return JsonResponse("TOKEN : [x] Delete -> Successful.", safe=False)
    
    else:
        return JsonResponse("[x] Invalid Method. (use POST/GET/PUT/DELETE)", safe=False)