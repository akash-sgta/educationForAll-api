from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib import messages

# --------------------------------------------------------------------------

from auth_prime.models import User_Credential
from auth_prime.models import User_Profile
from auth_prime.models import Admin_Privilege
from auth_prime.models import Admin_Credential
from auth_prime.models import Admin_Cred_Admin_Prev_Int
from auth_prime.models import User_Token_Table
from auth_prime.models import Api_Token_Table

from auth_prime.serializer import User_Credential_Serializer
from auth_prime.serializer import User_Profile_Serializer
from auth_prime.serializer import Admin_Privilege_Serializer
from auth_prime.serializer import Admin_Credential_Serializer

from auth_prime.authorize import Authorize, Cookie

# --------------------------------------------------------------------------

auth = Authorize()
API_VERSION = '1.0'

# -------------------------------API_SPACE-------------------------------------

# -----------------------------------------------------------------------------

@csrf_exempt
def user_credential_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        data_returned = dict()

        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = 'Method not supported : GET.'
        return JsonResponse(data_returned, safe=True)

    elif(request.method.upper() == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = str(ex)
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = data[1]
                    return JsonResponse(data_returned, safe=True)

                else:

                    try:

                        if(incoming_data["action"].upper() == "SIGNUP"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                            
                            try:
                                incoming_data = incoming_data["data"]
                                user_credential_de_serialized = User_Credential_Serializer(data = incoming_data["data"])
                            
                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 404
                                data_returned['message'] = str(ex)
                                return JsonResponse(data_returned, safe=True)
                            
                            else:
                                user_credential_de_serialized.initial_data['user_email'] = user_credential_de_serialized.initial_data['user_email'].lower()
                                user_credential_ref = User_Credential.objects.filter(user_email = user_credential_de_serialized.initial_data['user_email'])

                                if(len(user_credential_ref) > 0):
                                    data_returned['return'] = False
                                    data_returned['code'] = 104
                                    data_returned['message'] = "Wrong Credentials provided."
                                    
                                else:

                                    try:
                                        auth.user_email = user_credential_de_serialized.initial_data['user_email']
                                        auth.user_password = user_credential_de_serialized.initial_data['user_password']

                                    except Exception as ex:
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = str(ex)
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        data = auth.create_password_hashed()
                        
                                        if(data[0] == False):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = data[1]
                                            return JsonResponse(data_returned, safe=True)

                                        else:
                                            user_credential_de_serialized.initial_data['user_password'] = data[1] # successfully hashed password
                                            if(user_credential_de_serialized.is_valid()):
                                                user_credential_de_serialized.save()
                                                
                                                data = auth.sanction_authorization()
                                            
                                                if(data[0] == False):
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 404
                                                    data_returned['message'] = data[1]
                                                    return JsonResponse(data_returned, safe=True)
                                                    
                                                else:
                                                    data_returned['return'] = True
                                                    data_returned['code'] = 100
                                                    data_returned['data'] = {'hash' : data[1]}
                        
                                            else:
                                                data_returned['return'] = False
                                                data_returned['code'] = 405
                                                data_returned['message'] = user_credential_de_serialized.errors
                                                return JsonResponse(data_returned, safe=True)
                            
                            return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() in ("SIGNIN","LOGIN")):
                            data_returned['action'] += "-"+incoming_data["action"].upper()

                            try:
                                incoming_data = incoming_data['data']
                                auth.user_email = incoming_data['data']['user_email'].lower()
                                auth.user_password = incoming_data['data']['user_password']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 404
                                data_returned['message'] = str(ex)
                                return JsonResponse(data_returned, safe=True)
                            
                            else:
                                data = auth.sanction_authorization()
                    
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 404
                                    data_returned['message'] = data[1]
                                    return JsonResponse(data_returned, safe=True)

                                else:
                                    data_returned['return'] = True
                                    data_returned['code'] = 100
                                    data_returned['data'] = {'hash' : data[1]}

                            return JsonResponse(data_returned, safe=True)

                        elif(incoming_data['action'].upper() in ("SIGNOUT","LOGOUT")):
                            data_returned['action'] += "-"+incoming_data["action"].upper()

                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                            
                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 404
                                data_returned['message'] = str(ex)
                                return JsonResponse(data_returned, safe=True)
                            
                            else:
                                if('user_id' not in incoming_data.keys()): # user logging out self
                                    data = auth.check_authorization("user")

                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 102
                                        data_returned['message'] = data[1]
                                        return JsonResponse(data_returned, safe=True)

                                    else:
                                        token_table_ref = User_Token_Table.objects.filter(user_credential_id = int(data[1]))
                                        token_table_ref = token_table_ref[0]
                                        token_table_ref.delete()

                                        data_returned['return'] = True
                                        data_returned['code'] = 100
                    
                                else: # admin_prime deleting all or selected logins
                                    data = auth.check_authorization("admin", "prime")

                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 110
                                        data_returned['message'] = data[1]
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        user_ids = incoming_data['user_id']
                                        if(0 in user_ids):
                                            User_Token_Table.objects.all().delete() # closest command to truncate

                                            data_returned['return'] = True
                                            data_returned['code'] = 100
                                
                                        else:
                                            data_returned['return'] = list()
                                            data_returned['code'] = list()
                                            data_returned['message'] = list()
                                
                                            for id in user_ids:
                                                try:
                                                    token_table_ref = User_Token_Table.objects.filter(user_credential_id = int(id))
                                                
                                                except Exception as ex:
                                                    data_returned['return'].append(False)
                                                    data_returned['code'].append(404)
                                                    data_returned['message'].append(str(ex))
                                                    return JsonResponse(data_returned, safe=True)
                                                
                                                else:
                                                    if(len(token_table_ref) < 1):
                                                        data_returned['return'].append(False)
                                                        data_returned['code'].append(121)
                                                        data_returned['message'].append("USER id not logged in.")

                                                    else:
                                                        token_table_ref = token_table_ref[0]
                                                        token_table_ref.delete()

                                                        data_returned['return'].append(True)
                                                        data_returned['code'].append(100)
                                                        data_returned['message'].append(None)
                    
                            return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "Invalid action."
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'DELETE'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_api = user_data["api"]
            incoming_data = user_data["data"]

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        else:
            auth.api = incoming_api
            data = auth.check_authorization(api_check=True)

            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 150
                data_returned['message'] = data[1]
                return JsonResponse(data_returned, safe=True)

            else:
                try:
                    incoming_data = incoming_data['data']
                    auth.token = incoming_data["hash"]
                
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = str(ex)
                    return JsonResponse(data_returned, safe=True)

                else:
                    if('user_id' in incoming_data.keys()): # prime admin deleting others
                        data = auth.check_authorization("admin", "prime")

                        if(data[0] == False):
                            data_returned['return'] = False
                            data_returned['code'] = 110
                            data_returned['message'] = data[1]
                            return JsonResponse(data_returned, safe=True)
                        
                        else:
                            user_ids = incoming_data['user_id']
                            
                            if(0 in user_ids): # 0 -> delete all
                                user_credential_ref = User_Credential.objects.all().exclude(user_credential_id = int(data[1]))

                                if(len(user_credential_ref) < 1):
                                    data_returned['return'] = False
                                    data_returned['code'] = 404
                                    data_returned['message'] = "Already empty tray of USER CREDENTIALS."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    for individual in user_credential_ref:
                                        individual.delete()

                                    data_returned['return'] = True
                                    data_returned['code'] = 100
                                    data_returned['message'] = "All users(-1) deleted."
                            
                            else: # individual id deletes
                                data_returned['return'] = list()
                                data_returned['code'] = list()
                                data_returned['message'] = list()

                                for id in user_ids:
                                    try:
                                        if(int(id) == int(data[1])):
                                            data_returned['return'].append(False)
                                            data_returned['code'].append(404)
                                            data_returned['message'].append("Self Delete not applicable in this mode.") #SECURITY check

                                        else:
                                            try:
                                                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                            
                                            except Exception as ex:
                                                data_returned['return'].append(False)
                                                data_returned['code'].append(404)
                                                data_returned['message'].append(str(ex))
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                if(len(user_credential_ref) < 1):
                                                    data_returned['return'].append(False)
                                                    data_returned['code'].append(114)
                                                    data_returned['message'].append("USER id invalid")
                                                
                                                else:
                                                    user_credential_ref = user_credential_ref[0]
                                                    user_credential_ref.delete()

                                                    data_returned['return'].append(True)
                                                    data_returned['code'].append(100)
                                                    data_returned['message'].append(None)
                                    
                                    except Exception as ex:
                                        data_returned['return'].append(False)
                                        data_returned['code'].append(404)
                                        data_returned['message'].append(str(ex))
                                        continue
                                    
                                    else:
                                        continue

                    else: # user self delete
                        data = auth.check_authorization("user")
                
                        if(data[0] == False):
                            data_returned['return'] = False
                            data_returned['code'] = 102
                            data_returned['message'] = data[1]
                            return JsonResponse(data_returned, safe=True)
                        
                        else:
                            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

                            if(user_credential_ref.user_profile_id not in (None, "")):
                                user_credential_ref.user_profile_id.delete()

                            user_credential_ref.delete()

                            data_returned['return'] = True
                            data_returned['code'] = 100
        
                return JsonResponse(data_returned, safe=True)

    elif(request.method == 'PUT'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_api = user_data["api"]
            incoming_data = user_data["data"]

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        else:
            auth.api = incoming_api
            data = auth.check_authorization(api_check=True)

            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 150
                data_returned['message'] = data[1]
                return JsonResponse(data_returned, safe=True)

            else:
                try:
                    incoming_data = incoming_data['data']
                    auth.token = incoming_data["hash"]
                
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = str(ex)
                    return JsonResponse(data_returned, safe=True)

                else:
                    data = auth.check_authorization("user") # only self change applicable for now
                    
                    if(data[0] == False):
                        data_returned['return'] = False
                        data_returned['code'] = 102
                        data_returned['message'] = "User hash unauthorized."
                        return JsonResponse(data_returned, safe=True)

                    else:
                        user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))            
                        user_credential_de_serialized = User_Credential_Serializer(user_credential_ref,
                                                                                   data = incoming_data['data'])
                        
                        flag = False
                        if("user_email" in user_credential_de_serialized.initial_data.keys()):
                            email_temp = user_credential_de_serialized.initial_data['user_email'].lower()
                            user_credential_ref_temp = User_Credential.objects.filter(user_email = email_temp)

                            if(len(user_credential_ref_temp) > 0):
                                user_credential_ref_temp = user_credential_ref_temp[0]

                                if(user_credential_ref_temp.user_credential_id != user_credential_ref.user_credential_id):
                                    data_returned['return'] = False
                                    data_returned['code'] = 104
                                    data_returned['message'] = "User Email exists, can not be used."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    pass
                            
                            else:
                                pass

                        email_temp = user_credential_ref.user_email.lower()
                        user_credential_de_serialized.initial_data['user_email'] = email_temp
                    
                        # necessary fields for serializer but can not be given permission to user
                        user_credential_de_serialized.initial_data['user_password'] = user_credential_ref.user_password
                        user_credential_de_serialized.initial_data['user_security_question'] = user_credential_ref.user_security_question
                        user_credential_de_serialized.initial_data['user_security_answer'] = user_credential_ref.user_security_answer

                        if(user_credential_de_serialized.is_valid()):
                            user_credential_de_serialized.save()

                            data_returned['return'] = True
                            data_returned['code'] = 100
                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 405
                            data_returned['message'] = user_credential_de_serialized.errors

                    return JsonResponse(data_returned, safe=True)

    elif(request.method == 'FETCH'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_api = user_data["api"]
            incoming_data = user_data["data"]

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        else:
            auth.api = incoming_api
            data = auth.check_authorization(api_check=True)

            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 150
                data_returned['message'] = data[1]
                return JsonResponse(data_returned, safe=True)

            else:
                try:
                    incoming_data = incoming_data['data']
                    auth.token = incoming_data["hash"]
                
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = str(ex)
                    return JsonResponse(data_returned, safe=True)

                else:
                    if('user_id' not in incoming_data.keys()): # self fetch
                        data = auth.check_authorization("user")

                        if(data[0] == False):
                            data_returned['return'] = False
                            data_returned['code'] = 102
                            data_returned['message'] = "USER hash not authorized."
                            return JsonResponse(data_returned, safe=True)

                        else:
                            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                    
                            data_returned['return'] = True
                            data_returned['code'] = 100
                            data_returned['data'] = User_Credential_Serializer(user_credential_ref, many=False).data
                    
                            # initially not handed to user for security purposes
                            del(data_returned['data']['user_password'])
                            del(data_returned['data']["user_security_question"])
                            del(data_returned['data']["user_security_answer"])
                    
                    else: # fetching as an prime admin
                        data = auth.check_authorization("admin", "prime")

                        if(data[0] == False):
                            data_returned['return'] = False
                            data_returned['code'] = 110
                            data_returned['message'] = "ADMIN hash not authorized."
                            return JsonResponse(data_returned, safe=True)

                        else:
                            user_ids = incoming_data['user_id']

                            if(0 in user_ids): # 0 -> fetch all
                                data_returned['return'] = list()
                                data_returned['code'] = list()
                                data_returned['data'] = list()
                                data_returned['message'] = list()

                                user_credential_ref = User_Credential.objects.all()

                                if(len(user_credential_ref) < 1):
                                    data_returned['return'] = False
                                    data_returned['code'] = 404
                                    data_returned['message'] = "Already empty tray of USER CREDENTIALS."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    user_credential_serialized = User_Credential_Serializer(user_credential_ref, many=True).data
                                    
                                    for user in user_credential_serialized:
                                        data_returned['return'].append(True)
                                        data_returned['code'].append(100)
                                        data_returned['message'].append(None)

                                        if(int(user['user_credential_id']) == int(data[1])):
                                            key = "self"
                                        else:
                                            key = int(user['user_credential_id'])
                                        
                                        data_returned['data'].append({key : user})

                                        del(data_returned['data'][-1][id]['user_password'])
                                        del(data_returned['data'][-1][id]["user_security_question"])
                                        del(data_returned['data'][-1][id]["user_security_answer"])
                            
                            else: # fetch using using ids
                                data_returned['return'] = list()
                                data_returned['code'] = list()
                                data_returned['data'] = list()
                                data_returned['message'] = list()

                                for id in user_ids:

                                    try:
                                        user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                    
                                    except Exception as ex:
                                        data_returned['return'].append(False)
                                        data_returned['code'].append(404)
                                        data_returned['message'].append(str(ex))
                                        data_returned['data'].append(None)
                                    
                                    else:
                                        if(len(user_credential_ref) < 1):
                                            data_returned['return'].append(False)
                                            data_returned['code'].append(114)
                                            data_returned['message'].append("Wrong USER ID.")
                                            data_returned['data'].append(None)

                                        else:
                                            user_credential_ref = user_credential_ref[0]
                                            user_credential_serialized = User_Credential_Serializer(user_credential_ref, many=False).data
                                        
                                            data_returned['return'].append(True)
                                            data_returned['code'].append(100)
                                            data_returned['message'].append(None)

                                            if(int(user_credential_serialized['user_credential_id']) == int(data[1])):
                                                id = "self"
                                            else:
                                                id = int(user_credential_serialized['user_credential_id'])
                                            
                                            data_returned['data'].append({id : user_credential_serialized})

                                            del(data_returned['data'][-1][id]['user_password'])
                                            del(data_returned['data'][-1][id]["user_security_question"])
                                            del(data_returned['data'][-1][id]["user_security_answer"])

                    return JsonResponse(data_returned, safe=True)
    
    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "Parent action invalid."

        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def user_profile_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = 'Method not supported : GET.'
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = str(ex)
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = data[1]
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:
                        incoming_data = incoming_data['data']
                        auth.token = incoming_data['hash']

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)
                    
                    else:
                        data = auth.check_authorization("user")
        
                        if(data[0] == False):
                            data_returned['return'] = False
                            data_returned['code'] = 102
                            data_returned['message'] = "Invalid HASH."
                            return JsonResponse(data_returned, safe=True)

                        else:
                            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                            
                            if(user_credential_ref.user_profile_id in (None, "")):

                                try:
                                    user_profile_de_serialized = User_Profile_Serializer(data = incoming_data['data'])

                                except Exception as ex:
                                    data_returned['return'] = False
                                    data_returned['code'] = 404
                                    data_returned['message'] = str(ex)
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    if(("prime" in user_profile_de_serialized.initial_data.keys())
                                    and (user_profile_de_serialized.initial_data["prime"] == True)): # if student then roll number required
                                        if(("user_roll_number" in user_profile_de_serialized.initial_data.keys())
                                        and (user_profile_de_serialized.initial_data["user_roll_number"] in (None, ""))):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = "User profile of students need roll number to be filled."
                                            return JsonResponse(data_returned, safe=True)
                
                                    if(user_profile_de_serialized.is_valid()):
                                        user_profile_de_serialized.save()

                                        user_profile_ref = User_Profile.objects.latest('user_profile_id')
                                        user_credential_ref.user_profile_id = user_profile_ref
                                        user_credential_ref.save()

                                        data_returned['return'] = True
                                        data_returned['code'] = 100
                                    
                                    else:
                                        data_returned['return'] = False
                                        data_returned['code'] = 405
                                        data_returned['message'] = user_profile_de_serialized.errors
                                        return JsonResponse(data_returned, safe=True)
            
                            else:
                                data_returned['return'] = False
                                data_returned['code'] = 105
                                data_returned['message'] = "User already has a profile."
                                return JsonResponse(data_returned, safe=True)

                        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'DELETE'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = str(ex)
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = data[1]
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:
                        incoming_data = incoming_data['data']
                        auth.token = incoming_data['hash']

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)
                    
                    else:
                        data = auth.check_authorization("user")

                        if(data[0] == False):
                            data_returned['return'] = False
                            data_returned['code'] = 102
                            data_returned['message'] = "Invalid HASH."
                            return JsonResponse(data_returned, safe=True)
                        
                        else:
                            self_user_profile_ref = User_Credential.objects.get(user_credential_id = int(data[1])).user_profile_id

                            if('user_id' in incoming_data.keys()): # admin prime deleting other users(-1) profile
                                data = auth.check_authorization("admin", "prime")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = "USER not PRIME ADMIN."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    user_ids = incoming_data['user_id']

                                    if(0 in user_ids): # all at once

                                        if(self_user_profile_ref == None):
                                            user_profile_ref = User_Profile.objects.all()
                                        
                                        else:
                                            user_profile_ref = User_Profile.objects.all().exclude(user_profile_id = int(self_user_profile_ref.user_profile_id))
                                        
                                        if(len(user_profile_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = "Already empty tray of USER PROFILES."
                                        
                                        else:
                                            for user in user_profile_ref:
                                                user.delete()
                                            
                                            data_returned['return'] = True
                                            data_returned['code'] = 100
                                            data_returned['message'] = "All(-1) PROFILES deleted."

                                    else: # individual id_profile delete
                                        data_returned['return'] = list()
                                        data_returned['code'] = list()
                                        data_returned['message'] = list()

                                        for id in user_ids:
                                            try:
                                                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                            
                                            except Exception as ex:
                                                data_returned['return'].append(False)
                                                data_returned['code'].append(404)
                                                data_returned['message'].append(str(ex))
                                            
                                            else:
                                                if(len(user_credential_ref) < 1):
                                                    data_returned['return'].append(False)
                                                    data_returned['code'].append(114)
                                                    data_returned['message'].append("Invalid USER id.")
                                                
                                                else:
                                                    user_credential_ref = user_credential_ref[0]

                                                    if(user_credential_ref.user_profile_id in (None, "")):
                                                        data_returned['return'].append(False)
                                                        data_returned['code'].append(106)
                                                        data_returned['message'].append("USER PROFILE does not exist.")
                                                    
                                                    else:

                                                        if(self_user_profile_ref.user_profile_id == user_credential_ref.user_profile_id.user_profile_id):
                                                            data_returned['message'].append("self profile delete")

                                                        else:
                                                            data_returned['message'].append(None)

                                                        user_credential_ref.user_profile_id.delete()
                                                        data_returned['return'].append(True)
                                                        data_returned['code'].append(100)
                                                    

                            else: # self deleting profile

                                if(self_user_profile_ref == None):
                                    data_returned['return'] = False
                                    data_returned['code'] = 106
                                    data_returned['message'] = "USER does not have PROFILE."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    self_user_profile_ref.delete()
                                    data_returned['return'] = True
                                    data_returned['code'] = 100

                        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'PUT'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = str(ex)
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = data[1]
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:
                        incoming_data = incoming_data['data']
                        auth.token = incoming_data['hash']

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)
                    
                    else:
                        data = auth.check_authorization("user")

                        if(data[0] == False):
                            data_returned['return'] = False
                            data_returned['code'] = 102
                            data_returned['message'] = "Invalid HASH."
                            return JsonResponse(data_returned, safe=True)
                        
                        else:
                            self_user_profile_ref = User_Credential.objects.get(user_credential_id = int(data[1])).user_profile_id

                            if(self_user_profile_ref == None):
                                data_returned['return'] = False
                                data_returned['code'] = 106
                                data_returned['message'] = "USER PROFILE not found."
                                return JsonResponse(data_returned, safe=True)
                            
                            else:
                                
                                try:
                                    user_profile_de_serialized = User_Profile_Serializer(self_user_profile_ref, data = incoming_data['data'])
                                
                                except Exception as ex:
                                    data_returned['return'] = False
                                    data_returned['code'] = 404
                                    data_returned['message'] = str(ex)
                                    return JsonResponse(data_returned, safe=True)

                                else:
                                    if(("prime" in user_profile_de_serialized.initial_data.keys())
                                    and (user_profile_de_serialized.initial_data["prime"] == True)): # if student then roll number required
                                        if(("user_roll_number" in user_profile_de_serialized.initial_data.keys())
                                        and (user_profile_de_serialized.initial_data["user_roll_number"] in (None, ""))):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = "student profile requires university roll number."
                                            return JsonResponse(data_returned, safe=True)
                
                                    user_profile_de_serialized.initial_data["user_profile_id"] = self_user_profile_ref.user_profile_id
                                    
                                    if(user_profile_de_serialized.is_valid()):
                                        user_profile_de_serialized.save()

                                        data_returned['return'] = True
                                        data_returned['code'] = 100
                                    
                                    else:
                                        data_returned['return'] = False
                                        data_returned['code'] = 405
                                        data_returned['message'] = user_profile_de_serialized.errors
                                        return JsonResponse(data_returned, safe=True)

                        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'FETCH'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = str(ex)
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = data[1]
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:
                        incoming_data = incoming_data['data']
                        auth.token = incoming_data['hash']

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)
                    
                    else:
                        data = auth.check_authorization("user")

                        if(data[0] == False):
                            data_returned['return'] = False
                            data_returned['code'] = 102
                            data_returned['message'] = "Invalid HASH."
                            return JsonResponse(data_returned, safe=True)
                        
                        else:
                            self_user_profile_ref = User_Credential.objects.get(user_credential_id = int(data[1])).user_profile_id

                            if('user_id' in incoming_data.keys()): # user fetching other user_profiles
                                user_ids = incoming_data['user_id']

                                if(0 in user_ids): # all at once
                                    user_profile_ref = User_Profile.objects.all()
                                        
                                    if(len(user_profile_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = "Already empty tray of USER PROFILES."
                                        
                                    else:
                                        user_profile_serialized = User_Profile_Serializer(user_profile_ref, many=True).data
                                        data_returned['return'] = list()
                                        data_returned['code'] = list()
                                        data_returned['data'] = list()
                                        data_returned['message'] = list()

                                        for user in user_profile_serialized:
                                            if(user['user_profile_id'] == self_user_profile_ref.user_profile_id):
                                                key = "self"
                                            else:
                                                key = int(user['user_profile_id'])
                                            
                                            data_returned['return'].append(True)
                                            data_returned['code'].append(100)
                                            data_returned['data'].append({key : user})
                                            data_returned['message'] = None

                                else: # individual id_profile fetch
                                    data_returned['return'] = list()
                                    data_returned['code'] = list()
                                    data_returned['message'] = list()
                                    data_returned['data'] = list()

                                    for id in user_ids:
                                        try:
                                            user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                            
                                        except Exception as ex:
                                            data_returned['return'].append(False)
                                            data_returned['code'].append(404)
                                            data_returned['message'].append(str(ex))
                                            data_returned['data'].append(None)
                                            
                                        else:
                                            if(len(user_credential_ref) < 1):
                                                data_returned['return'].append(False)
                                                data_returned['code'].append(114)
                                                data_returned['message'].append("Invalid USER id.")
                                                data_returned['data'].append(None)
                                                
                                            else:
                                                user_credential_ref = user_credential_ref[0]

                                                if(user_credential_ref.user_profile_id in (None, "")):
                                                    data_returned['return'].append(False)
                                                    data_returned['code'].append(106)
                                                    data_returned['message'].append("USER PROFILE does not exist.")
                                                    data_returned['data'].append(None)
                                                    
                                                else:
                                                    user_profile_serialized = User_Profile_Serializer(user_credential_ref.user_profile_id, many=False).data

                                                    if(self_user_profile_ref.user_profile_id == user_profile_serialized['user_profile_id']):
                                                        key = "self"
                                                    else:
                                                        key = int(user_profile_serialized['user_profile_id'])

                                                    data_returned['data'].append({key : user_profile_serialized})
                                                    data_returned['return'].append(True)
                                                    data_returned['code'].append(100)
                                                    data_returned['message'].append(None)
                            
                            else: # self fetch profile

                                if(self_user_profile_ref == None):
                                    data_returned['return'] = False
                                    data_returned['code'] = 106
                                    data_returned['message'] = "USER does not have PROFILE."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    user_profile_serialized = User_Profile_Serializer(self_user_profile_ref, many=False).data
                                    data_returned['return'] = True
                                    data_returned['code'] = 100
                                    data_returned['data'] = user_profile_serialized

                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "parent action invalid."

        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def admin_credential_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'POST'):
        data_returned['action'] = request.method.upper()

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_data = user_data["data"]
            incoming_hash = incoming_data["hash"]
            incoming_data = incoming_data["data"]
            incoming_api_version = user_data["api_v"]
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        if(incoming_api_version == API_VERSION):
            pass
        else:
            data_returned['return'] = False
            data_returned['code'] = 406

            return JsonResponse(data_returned, safe=True)

        try:
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.check_authorization("admin", "prime") #only prime admins can grant admin access
        
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 110
        else:
            try:
                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(incoming_data["user_credential_id"]))
            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 404
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            if(len(user_credential_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 114
            else:
                try:
                    admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(incoming_data["user_credential_id"]))
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = str(ex)

                    return JsonResponse(data_returned, safe=True)
            
                if(len(admin_credential_ref) > 0):
                    data_returned['return'] = False
                    data_returned['code'] = 112
                else:
                    user_credential_ref = user_credential_ref[0]
                    admin_credential_ref_new = Admin_Credential(user_credential_id = user_credential_ref)
                    admin_credential_ref_new.save()

                    data_returned['return'] = True
                    data_returned['code'] = 100
    
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'DELETE'):
        data_returned['action'] = request.method.upper()

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_data = user_data["data"]
            incoming_hash = incoming_data["hash"]
            incoming_api_version = user_data["api_v"]
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        if(incoming_api_version == API_VERSION):
            pass
        else:
            data_returned['return'] = False
            data_returned['code'] = 406

            return JsonResponse(data_returned, safe=True)

        try:
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.check_authorization("admin") #prime admins can remove other admins and self removal is permitted
        
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 111
        else:
            if("data" in incoming_data.keys()): # admin prime revoking others
                incoming_data = incoming_data['data']
                
                if("user_credential_id" in incoming_data.keys()): # admin prime revoking others
                    data = auth.check_authorization("admin", "prime")
                    
                    if(data[0] == False):
                        data_returned['return'] = False
                        data_returned['code'] = 110
                        flag = False,0

                    else:
                        temp = int(incoming_data["user_credential_id"])
                        flag = True,113
            else: # self revoke
                temp = int(data[1])
                flag = True,111
            
            if(flag[0] == True):
                admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = temp)
                if(len(admin_credential_ref) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = flag[1]
                else:
                    admin_credential_ref = admin_credential_ref[0]
                    admin_credential_ref.delete()

                    data_returned['return'] = True
                    data_returned['code'] = 100
    
        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'PUT'):
        data_returned['action'] = request.method.upper()

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_data = user_data["data"]
            incoming_hash = incoming_data["hash"]
            incoming_data = incoming_data["data"]
            privileges = incoming_data["privileges"]
            incoming_api_version = user_data["api_v"]
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        if(incoming_api_version == API_VERSION):
            pass
        else:
            data_returned['return'] = False
            data_returned['code'] = 406

            return JsonResponse(data_returned, safe=True)

        try:
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.check_authorization("admin") #prime admins can change other admins and self change is permitted
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 111
        else:
            if("user_credential_id" in incoming_data.keys()): # admin prime change others
                data = auth.check_authorization("admin", "prime")
                    
                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 110
                    flag = False,0
                else:
                    temp = int(incoming_data["user_credential_id"])
                    flag = True,113
            
            else: # admin change self
                temp = int(data[1])
                flag = True,111
            
            if(flag[0] == True):
                admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = temp)
                if(len(admin_credential_ref) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = flag[1]
                else:
                    admin_credential_ref = admin_credential_ref[0]
                    
                    try:
                        data_returned['return'] = list()
                        data_returned['code'] = list()

                        for prev_id in privileges:
                            if(int(prev_id) < 0):
                                flag = False
                                prev_id *= -1
                            else:
                                flag = True
                            
                            many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id,
                                                                                        admin_privilege_id = int(prev_id))
                            if(len(many_to_many_ref) > 0):
                                if(flag == True):
                                    data_returned['return'].append(False)
                                    data_returned['code'].append(115)
                                else:
                                    many_to_many_ref = many_to_many_ref[0]
                                    many_to_many_ref.delete()

                                    data_returned['return'].append(True)
                                    data_returned['code'].append(100)
                            else:
                                admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(prev_id))
                                if(len(admin_privilege_ref) < 1):
                                    data_returned['return'].append(False)
                                    data_returned['code'].append(116)
                                else:
                                    admin_privilege_ref = admin_privilege_ref[0]
                                    many_to_many_ref_new = Admin_Cred_Admin_Prev_Int(admin_credential_id = admin_credential_ref,
                                                                                     admin_privilege_id = admin_privilege_ref)
                                    many_to_many_ref_new.save()

                                    data_returned['return'].append(True)
                                    data_returned['code'].append(100)

                    except Exception as ex:
                        data_returned['return'].append(False)
                        data_returned['code'].append(404)
                        data_returned['return'] = tuple(data_returned['return'])
                        data_returned['code'] = tuple(data_returned['code'])
                        data_returned['message'] = str(ex)

                        return JsonResponse(data_returned, safe=True)
                    else:
                        data_returned['return'] = tuple(data_returned['return'])
                        data_returned['code'] = tuple(data_returned['code'])

        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'FETCH'):
        data_returned['action'] = request.method.upper()

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_data = user_data["data"]
            incoming_hash = incoming_data["hash"]
            incoming_data = incoming_data["data"]
            incoming_api_version = user_data["api_v"]
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        if(incoming_api_version == API_VERSION):
            pass
        else:
            data_returned['return'] = False
            data_returned['code'] = 406

            return JsonResponse(data_returned, safe=True)

        try:
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.check_authorization("admin")
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 111
        else:
            if("user_credential_id" in incoming_data.keys()): # admin prime fetch others
                data = auth.check_authorization("admin", "prime")
                    
                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 110
                    flag = False,0
                else:
                    temp = int(incoming_data["user_credential_id"])
                    flag = True,113
            
            else: # admin fetch self
                temp = int(data[1])
                flag = True,111
                
            if(flag[0] == True):
                admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(temp))
                if(len(admin_credential_ref) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = flag[1]
                else:
                    admin_credential_ref = admin_credential_ref[0]
                    many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id)

                    data_returned['return'] = True
                    data_returned['code'] = 100
                    data_returned['data'] = dict()

                    for query in many_to_many_ref:
                        admin_privilege_ref = Admin_Privilege.objects.get(admin_privilege_id = query.admin_privilege_id.admin_privilege_id)
                        admin_privilege_serialized = Admin_Privilege_Serializer(admin_privilege_ref, many=False)
                        if(temp == data[1]):
                            data_returned['data']["self"] = admin_privilege_serialized.data
                        else:
                            data_returned['data'][int(temp)] = admin_privilege_serialized.data

        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def admin_privilege_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'POST'):
        data_returned['action'] = request.method.upper()

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_data = user_data["data"]
            incoming_hash = incoming_data["hash"]
            incoming_data = incoming_data["data"]
            incoming_api_version = user_data["api_v"]
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        if(incoming_api_version == API_VERSION):
            pass
        else:
            data_returned['return'] = False
            data_returned['code'] = 406

            return JsonResponse(data_returned, safe=True)

        try:
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.check_authorization("admin", "prime") #only prime admins can grant admin access
        
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 110
        else:
            try:
                admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = incoming_data["admin_privilege_name"].upper())
            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 404
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            if(len(admin_privilege_ref) > 0):
                data_returned['return'] = False
                data_returned['code'] = 117
            else:
                admin_privilege_de_serialized = Admin_Privilege_Serializer(data=incoming_data)
                if(admin_privilege_de_serialized.is_valid()):
                    admin_privilege_de_serialized.save()

                    data_returned['return'] = True
                    data_returned['code'] = 100
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 405
                    data_returned['message'] = admin_privilege_de_serialized.errors
        
        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'DELETE'):
        data_returned['action'] = request.method.upper()

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_data = user_data["data"]
            incoming_hash = incoming_data["hash"]
            incoming_privilege_id = incoming_data["admin_privilege_id"]
            incoming_api_version = user_data["api_v"]
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        if(incoming_api_version == API_VERSION):
            pass
        else:
            data_returned['return'] = False
            data_returned['code'] = 406

            return JsonResponse(data_returned, safe=True)

        try:
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.check_authorization("admin", "prime") #prime admins can remove privileges
        
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 110
        else:
            admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(incoming_privilege_id))
            if(len(admin_privilege_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 116
            else:
                admin_privilege_ref = admin_privilege_ref[0]
                admin_privilege_ref.delete()

                data_returned['return'] = True
                data_returned['code'] = 100
        
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'FETCH'):
        data_returned['action'] = request.method.upper()

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_data = user_data["data"]
            incoming_hash = incoming_data["hash"]
            incoming_privilege_ids = incoming_data["admin_privilege_id"]
            incoming_api_version = user_data["api_v"]
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 402
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        if(incoming_api_version == API_VERSION):
            pass
        else:
            data_returned['return'] = False
            data_returned['code'] = 406

            return JsonResponse(data_returned, safe=True)

        try:
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.check_authorization("admin") #all admins can see privileges
        
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 111
        else:
            if(0 in incoming_privilege_ids):
                admin_privilege_ref = Admin_Privilege.objects.all()
                admin_privilege_serialized = Admin_Privilege_Serializer(admin_privilege_ref, many=True)

                data_returned['return'] = True
                data_returned['code'] = 100
                data_returned['data'] = admin_privilege_serialized.data
            else:
                data_returned['return'] = list()
                data_returned['code'] = list()
                data_returned['data'] = list()

                for id in incoming_privilege_ids:
                    try:
                        admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(id))
                    except Exception as ex:
                        data_returned['return'].append(False)
                        data_returned['code'].append(404)
                        data_returned['data'].append(None)
                        data_returned['message'] = str(ex)

                        return JsonResponse(data_returned, safe=True)

                    if(len(admin_privilege_ref) < 1):
                        data_returned['return'].append(False)
                        data_returned['code'].append(116)
                        data_returned['data'].append(None)
                    else:
                        admin_privilege_serialized = Admin_Privilege_Serializer(admin_privilege_ref[0], many=False)
                        data_returned['return'].append(True)
                        data_returned['code'].append(100)
                        data_returned['data'].append(admin_privilege_serialized.data)
                


        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)

# ------------------------------VIEW_SPACE-------------------------------------

def api_token_web(request, word=None):
    global auth
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
            apit = Api_Token_Table.objects.get(pk = data[1])
            data_returned['user_name'] = apit.user_name.split()[0]
            data_returned['type'] = 'logged'.upper()
            data_returned['api_token'] = apit.user_key_private
            return cookie.set_authentication_info(request, 'auth_prime/api.html', data_returned, apit.pk)
        
        data_returned['type'] = type

        return render(request, 'auth_prime/api.html', data_returned)
    
    elif(request.method == 'POST'):
        temp = dict(request.POST)
        if(temp['form_type'][0] == 'signup'):
            keys = ['user_f_name', 'user_l_name', 'user_email', 'user_password']
            
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
                        apit = Api_Token_Table(user_name = f"{temp[keys[0]][0]} {temp[keys[1]][0]}",
                                        user_email = f"{temp[keys[2]][0].lower()}",
                                        user_password = f"{data[1]}",
                                        user_key_private = auth.random_generator())
                        apit.save()
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
                        apit = Api_Token_Table.objects.filter(user_email = f"{temp[keys[0]][0].lower()}",
                                                              user_password = data[1])
                        if(len(apit) < 1):
                            messages.add_message(request, messages.INFO, "Wrong Credentials ! Try again !")
                            data_returned['type'] = 'signin'.upper()
                            return render(request, 'auth_prime/api.html', data_returned)
                        else:
                            apit = apit[0]
                            data_returned['user_name'] = apit.user_name.split()[0]
                            data_returned['type'] = 'logged'.upper()
                            data_returned['api_token'] = apit.user_key_private
                            return cookie.set_authentication_info(request, 'auth_prime/api.html', data_returned, apit.pk)
                    except Exception as ex:
                        print(f"[x] API KEY LOGIN : {str(ex)}")
            
            return render(request, 'auth_prime/api.html', data_returned)
        
        elif(temp['form_type'][0] == 'signout'):

            data_returned['type'] = 'signin'.upper()
            return cookie.revoke_authentication_info(request, 'auth_prime/api.html', data_returned)
        
        else:
            return redirect('AUTH_TOKEN')

        