from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from auth_prime.models import User_Credential, Admin_Privilege, Admin_Credential, Token_Table
from auth_prime.serializer import User_Credential_Serializer, Admin_Privilege_Serializer, Admin_Credential_Serializer, Token_Table_Serializer

import json
from auth_prime.authorize import Authorize
# Create your views here.

auth = Authorize()

@csrf_exempt
def user_API(request, id=0):
    global auth
    data_returned = dict()

    if(request.method == 'FETCH'):
        data_returned['action'] = "FETCH"

        user_data = JSONParser().parse(request)
        incoming_action = user_data["action"]
        incoming_data = user_data["data"]

        if(incoming_action == 'get_one'):
            data_returned['action'] += '-GET_ONE'
            
            auth.clear()
            auth.token = incoming_data['hash']

            data = auth.is_authorized()

            if(data[0] == True):
                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(data[1]))
                if(len(user_credential_ref) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = 2001 # Invalid Hash, Clear and reHash
                    return JsonResponse(data_returned, safe=True)
                else:
                    user_credential_ref = user_credential_ref[0]
                    data_returned['return'] = True
                    data_returned['code'] = 1000 # No error encountered
                    data_returned['data'] = dict(User_Credential_Serializer(user_credential_ref, many=False).data)
                    del(data_returned['data']['user_password'])
                    del(data_returned['data']['user_credential_id'])
                    del(data_returned['data']["user_security_question"])
                    del(data_returned['data']["user_security_answer"])
                    return JsonResponse(data_returned, safe=True)
            else:
                data_returned['return'] = False
                data_returned['code'] = 9001 # Amiguous Error
                data_returned['message'] = data[1]
                return JsonResponse(data_returned, safe=True)                
        
        elif(incoming_action == 'get_all'):
            data_returned['action'] += '-GET_ALL'

            auth.clear()
            auth.token = incoming_data['hash']

            data = auth.is_authorized_admin()

            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 3002 # unauthorized admin access
                return JsonResponse(data_returned, safe=True)
            else:

                user_credential_ref = User_Credential.objects.all()
                user_credential_serialized = User_Credential_Serializer(user_credential_ref, many=True)
                data_returned['return'] = True
                data_returned['code'] = 1000

                data_returned['data'] = dict()
                i = 0
                for data in user_credential_serialized.data:
                    data_returned['data'][i] = dict(data)
                    del(data_returned['data'][i]['user_password'])
                    i += 1
                
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

            data_returned['action'] += "-SIGNUP"

            user_credential_de_serialized = User_Credential_Serializer(data=incoming_data)
            data_to_check = user_credential_de_serialized.initial_data
            data_to_check['user_email'] = (data_to_check['user_email']).lower()
            temp_fetch = User_Credential.objects.filter(user_email=data_to_check['user_email'])

            if(len(temp_fetch) > 0):
                data_returned['return'] = False
                data_returned['code'] = 1001 # User Email Exists
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.clear()
                auth.user_email = data_to_check['user_email'].lower()
                auth.user_password = data_to_check['user_password']
                
                data = auth.create_password_hashed()
                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 8001 # Amiguous Error
                    data_returned['message'] = data[1]
                    return JsonResponse(data_returned, safe=True)
                else:
                    user_credential_de_serialized.initial_data['user_password'] = data[1]
                    
                if(user_credential_de_serialized.is_valid()):
                    user_credential_de_serialized.save()

                    data_returned['return'] = True
                    data_returned['code'] = 1000 # No error encountered

                    data = auth.sanction_authorization()
                    if(data[0] == False):
                        data_returned['return'] = False
                        data_returned['code'] = 8001 # Amiguous Error
                        data_returned['message'] = data[1]
                        return JsonResponse(data_returned, safe=True)
                    else:
                        data_returned['data'] = dict()
                        data_returned['data']['hash'] = data[1]
                        return JsonResponse(data_returned, safe=True)
                
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 9001 # Amiguous Error
                    data_returned['message'] = user_credential_de_serialized.errors
                    return JsonResponse(data_returned, safe=True)

        elif(incoming_action == "login"):
            data_returned['action'] += "-LOGIN"

            auth.clear()
            auth.user_email = incoming_data['user_email'].lower()
            auth.user_password = incoming_data['user_password']

            data = auth.sanction_authorization()
            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 9001 # Amiguous Error
                data_returned['message'] = data[1]
            else:
                data_returned['return'] = True
                data_returned['code'] = 1000 # No error encountered
                data_returned['data'] = dict()
                data_returned['data']['hash'] = data[1]
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

            auth.clear()
            auth.token = incoming_data['hash']
            data = auth.is_authorized()
            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 2001 # hash not in db
                data_returned['message'] = data[1]
                return JsonResponse(data_returned, safe=True)
            else:
                user_credential_ref = User_Credential.objects.filter(user_credential_id=int(data[1]))[0]
                user_credential_de_serialized = User_Credential_Serializer(user_credential_ref, data=incoming_data['data'])

                temp = User_Credential.objects.filter(user_email=user_credential_de_serialized.initial_data['user_email'].lower())
                if(len(temp) > 0):
                    temp = temp[0]
                    if(temp.user_credential_id == user_credential_ref.user_credential_id):
                        user_credential_de_serialized.initial_data['user_email'] = user_credential_de_serialized.initial_data['user_email'].lower()
                        if(user_credential_de_serialized.initial_data['user_email'] != user_credential_ref.user_email):
                            auth.clear()
                            auth.token = incoming_data['hash']
                            auth.user_email = user_credential_de_serialized.initial_data['user_email']
                        
                        # necessary fields for serializer but can not be given permission to user
                        user_credential_de_serialized.initial_data['user_password'] = user_credential_ref.user_password
                        user_credential_de_serialized.initial_data['user_security_question'] = user_credential_ref.user_security_question
                        user_credential_de_serialized.initial_data['user_security_answer'] = user_credential_ref.user_security_answer
                    else:
                        data_returned['return'] = False
                        data_returned['code'] = 1001 # User Email Exists
                        return JsonResponse(data_returned, safe=True)
                else:
                    user_credential_de_serialized.initial_data['user_email'] = user_credential_de_serialized.initial_data['user_email'].lower()
                    
                    # necessary fields for serializer but can not be given permission to user
                    user_credential_de_serialized.initial_data['user_password'] = user_credential_ref.user_password
                    user_credential_de_serialized.initial_data['user_security_question'] = user_credential_ref.user_security_question
                    user_credential_de_serialized.initial_data['user_security_answer'] = user_credential_ref.user_security_answer

                if(user_credential_de_serialized.is_valid()):
                    user_credential_de_serialized.save()

                    data_returned['return'] = True
                    data_returned['code'] = 1000
                    return JsonResponse(data_returned, safe=True)
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 9001
                    data_returned['message'] = user_credential_de_serialized.errors
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

        if(incoming_action == 'one'):
            data_returned['action'] += "-ONE"

            auth.clear()
            auth.token = incoming_data['hash']
            data = auth.is_authorized()
            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 8001
                data_returned['message'] = data[1]
                return JsonResponse(data_returned, safe=True)
            else:
                user_credential_ref = User_Credential.objects.filter(user_credential_id=int(data[1]))
                user_credential_ref = user_credential_ref[0]
                user_credential_ref.delete()
                data_returned['return'] = True
                data_returned['code'] = 1000
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
                admins = Admin_Credential.objects.all()
                admins_serialized = Admin_Credential_Serializer(admins, many=True)
                return JsonResponse(admins_serialized.data, safe=False)
            else:
                admins = Admin_Credential.objects.get(admin_id=id)
                admins_serialized = Admin_Credential_Serializer(admins, many=False)
                return JsonResponse(admins_serialized.data, safe=False)
        except Exception as ex:
            print(f"[!] ADMIN API : GET : {ex}")
            return JsonResponse("ADMIN : [x] Data Get -> Unsuccessful.", safe=False)
    
    elif(request.method == 'POST'):
        admin_data = JSONParser().parse(request)
        admin_de_serialized = Admin_Credential_Serializer(data=admin_data)
        if(admin_de_serialized.is_valid()):
            admin_de_serialized.save()
            return JsonResponse("ADMIN : [.] Data Add -> Successful.", safe=False)
        else:
            return JsonResponse("ADMIN : [x] Data Add -> Unsuccessful.", safe=False)
    
    elif(request.method == 'PUT'):
        admin_data = JSONParser().parse(request)
        admin = Admin_Credential.objects.get(admin_id = admin_data['admin_id'])
        admin_de_serialized = Admin_Credential_Serializer(admin, data=admin_data)
        if(admin_de_serialized.is_valid()):
            admin_de_serialized.save()
            return JsonResponse("ADMIN : [.] Update -> Successful.", safe=False)
        else:
            return JsonResponse("ADMIN : [x] Update -> Unsuccessful.", safe=False)
    
    elif(request.method == 'DELETE'):
        try:
            admin = Admin_Credential.objects.get(admin_id=id)
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