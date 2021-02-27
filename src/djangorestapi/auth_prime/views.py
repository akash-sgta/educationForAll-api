from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

import logging
import re
# --------------------------------------------------------------------------

from auth_prime.models import User_Credential
from auth_prime.models import User_Profile
from auth_prime.models import Admin_Privilege
from auth_prime.models import Admin_Credential
from auth_prime.models import Admin_Cred_Admin_Prev_Int
from auth_prime.models import User_Token_Table
from auth_prime.models import Api_Token_Table
from auth_prime.models import Image

from auth_prime.serializer import User_Credential_Serializer
from auth_prime.serializer import User_Profile_Serializer
from auth_prime.serializer import Admin_Privilege_Serializer
from auth_prime.serializer import Admin_Credential_Serializer

from auth_prime.authorize import Authorize, Cookie

# --------------------------------------------------------------------------

auth = Authorize()
cookie = Cookie()

# -------------------------------API_SPACE-------------------------------------
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s | %(message)s')
def logger(api_key, message):
    logging.info(f"{api_key} -> {message}")
# -----------------------------------------------------------------------------

@csrf_exempt
def upload_image(request):
    global auth
    global cookie
    data_returned = dict()

    # @csrf_protect
    def post_it(request):
        if('auth' not in request.POST.keys()):
            return False, "No api auth token found."
        
        else:
            auth = request.POST.get('auth')
            api_token_ref = Api_Token_Table.objects.filter(user_key_private = auth)
            if(len(api_token_ref) < 1):
                return False, "INVALID : API token."
            
            else:
                if(len(request.FILES) < 1):
                    return False, "No files found"
                else:
                    image_file = request.FILES['image']
                    if(str(image_file.content_type).startswith("image")):
                        if(image_file.size < 5000000):
                            fs = FileSystemStorage()
                            file_name = fs.save(image_file.name, image_file)
                            file_url = fs.url(file_name)

                            image_ref = Image(image_url = file_url, image_name = file_name)
                            image_ref.save()
                            
                            print(True, image_ref.image_id)
                            return True, image_ref.image_id

                        else:
                            return False, "Size Error : Image size should be less than 5mb"
                    else:
                        return False, "Format Error : POST file should be Image"

    if(request.method == 'GET'):
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = 'Method not supported : GET.'
        return JsonResponse(data_returned, safe=True)


    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        data_returned['return'], message = post_it(request)

        if(data_returned['return'] == True):
            data_returned['code'] = 100
            data_returned['data'] = {"image_id" : message}
        
        else:
            data_returned['code'] = 404
            data_returned['message'] = message

        return JsonResponse(data_returned, safe=True)
    
    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "Parent action invalid"
        return JsonResponse(data_returned, safe=True)
  
@csrf_exempt
def user_credential_API(request):
    global auth
    data_returned = dict()

    if(request.method.upper() == 'GET'):
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
                                    data_returned['message'] = "Email Already registered."
                                    
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

                        elif(incoming_data['action'].upper()  == "DELETE"):
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
                                if('user_id' in incoming_data.keys()): # prime admin deleting others
                                    data_returned['data'] = dict()
                                    temp = dict()

                                    data = auth.check_authorization("admin", "prime")

                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 110
                                        data_returned['message'] = data[1]
                                        return JsonResponse(data_returned, safe=True)
                        
                                    else:
                                        user_ids = tuple(set(incoming_data['user_id']))
                            
                                        if(0 in user_ids): # 0 -> delete all
                                            user_credential_ref_all = User_Credential.objects.all().exclude(user_credential_id = int(data[1]))

                                            if(len(user_credential_ref_all) < 1):
                                                temp['return'] = False
                                                temp['code'] = 404
                                                temp['message'] = "Already empty tray of USER CREDENTIALS."
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()
                                                return JsonResponse(data_returned, safe=True)
                                
                                            else:
                                                user_credential_ref_all.delete()

                                                temp['return'] = True
                                                temp['code'] = 100
                                                temp['message'] = "All users(-1) deleted."
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()
                            
                                        else: # individual id deletes

                                            for id in user_ids:
                                                try:
                                                    if(int(id) == int(data[1])):
                                                        temp['return'] = False
                                                        temp['code'] = 404
                                                        temp['message'] = "Self Delete not applicable in this mode." #SECURITY check
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()

                                                    else:
                                                        try:
                                                            user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                            
                                                        except Exception as ex:
                                                            temp['return'] = False
                                                            temp['code'] = 404
                                                            temp['message'] = str(ex)
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()
                                            
                                                        else:
                                                            if(len(user_credential_ref) < 1):
                                                                temp['return'] = False
                                                                temp['code'] = 114
                                                                temp['message'] = "USER id invalid"
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                                
                                                            else:
                                                                user_credential_ref = user_credential_ref[0]
                                                                user_credential_ref.delete()

                                                                temp['return'] = True
                                                                temp['code'] = 100
                                                                temp['message'] = "SUCCESS : USER Credential Deleted."
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                    
                                                except Exception as ex:
                                                    temp['return'] = False
                                                    temp['code'] = 404
                                                    temp['message'] = str(ex)
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()
                                                
                                                finally:
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

                        elif(incoming_data['action'].upper()  == "EDIT"):
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

                        elif(incoming_data['action'].upper()  == "READ"):
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
                                    data_returned['data'] = dict()
                                    temp = dict()
                                    
                                    data = auth.check_authorization("admin", "prime")

                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 110
                                        data_returned['message'] = "ADMIN hash not authorized."
                                        return JsonResponse(data_returned, safe=True)

                                    else:
                                        user_ids = tuple(set(incoming_data['user_id']))

                                        if(len(user_ids) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = "Atleast one USER ID required."
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            if(0 in user_ids): # 0 -> fetch all
                                                user_credential_ref = User_Credential.objects.all()

                                                if(len(user_credential_ref) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 404
                                                    temp['message'] = "Already empty tray of USER CREDENTIALS."
                                                    data_returned['data'][0] = temp.copy()
                                                    temp.clear()
                                                    return JsonResponse(data_returned, safe=True)
                                    
                                                else:
                                                    user_credential_serialized = User_Credential_Serializer(user_credential_ref, many=True).data

                                                    temp['return'] = True
                                                    temp['code'] = 100
                                                    temp['data'] = list()

                                                    for user in user_credential_serialized:
                                                        if(int(user['user_credential_id']) == int(data[1])):
                                                            key = "self"
                                                        else:
                                                            key = int(user['user_credential_id'])

                                                        temp['data'].append({key : user})

                                                        del(temp['data'][-1][key]['user_password'])
                                                        del(temp['data'][-1][key]["user_security_question"])
                                                        del(temp['data'][-1][key]["user_security_answer"])

                                                    data_returned['data'][0] = temp.copy()
                                                    temp.clear()
                                
                                            else: # fetch using using ids
                                                for id in user_ids:
                                                    try:
                                                        user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                                    
                                                    except Exception as ex:
                                                        temp['return'] = False
                                                        temp['code'] = 404
                                                        temp['message'] = str(ex)
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                                    
                                                    else:
                                                        if(len(user_credential_ref) < 1):
                                                            temp['return'] = False
                                                            temp['code'] = 114
                                                            temp['message'] = "Wrong USER ID."
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()

                                                        else:
                                                            user_credential_ref = user_credential_ref[0]
                                                            user_credential_serialized = User_Credential_Serializer(user_credential_ref, many=False).data
                                                        
                                                            temp['return'] = True
                                                            temp['code'] = 100

                                                            # if(int(user_credential_serialized['user_credential_id']) == int(data[1])):
                                                            #     id = "self"
                                                            # else:
                                                            #     id = int(user_credential_serialized['user_credential_id'])
                                                            
                                                            temp['data'] = user_credential_serialized

                                                            del(temp['data']['user_password'])
                                                            del(temp['data']["user_security_question"])
                                                            del(temp['data']["user_security_answer"])

                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()

                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "Parent action invalid"
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

                        if(incoming_data["action"].upper() == "CREATE"):
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

                                                user_profile_ref = User_Profile.objects.get(user_profile_id = user_profile_de_serialized.data['user_profile_id'])
                                                user_credential_ref.user_profile_id = user_profile_ref
                                                user_credential_ref.save()

                                                data_returned['return'] = True
                                                data_returned['code'] = 100
                                                data_returned['message'] = "CREATE without IMAGE."

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
                    
                        elif(incoming_data["action"].upper() == "DELETE"):
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
                                                user_ids = tuple(set(incoming_data['user_id']))

                                                if(len(user_ids) < 1):
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 404
                                                    data_returned['message'] = "User ID empty."
                                                    return JsonResponse(data_returned, safe=True)
                                                
                                                else:
                                                    data_returned['data'] = dict()
                                                    temp = dict()

                                                    if(0 in user_ids): # all at once

                                                        if(self_user_profile_ref == None):
                                                            user_profile_ref_all = User_Profile.objects.all()
                                                        
                                                        else:
                                                            user_profile_ref_all = User_Profile.objects.all().exclude(user_profile_id = int(self_user_profile_ref.user_profile_id))
                                                        
                                                        if(len(user_profile_ref_all) < 1):
                                                            temp['return'] = False
                                                            temp['code'] = 404
                                                            temp['message'] = "Already empty tray of USER PROFILES."
                                                            data_returned['data'][0] = temp.copy()
                                                            temp.clear()
                                                            return JsonResponse(data_returned, safe=True)
                                                        
                                                        else:
                                                            for user in user_profile_ref_all:
                                                                if(user.user_pofile_pic in (None, "")):
                                                                    pass
                                                                else:
                                                                    fs = FileSystemStorage()
                                                                    fs.delete(user.user_pofile_pic.image_name)
                                                                    user.user_pofile_pic.delete()
                                                                
                                                                user.delete()
                                                            
                                                            temp['return'] = True
                                                            temp['code'] = 100
                                                            temp['message'] = "All(-1) PROFILES deleted."
                                                            data_returned['data'][0] = temp.copy()
                                                            temp.clear()

                                                    else: # individual id_profile delete
                                                        for id in user_ids:
                                                            try:
                                                                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                                            
                                                            except Exception as ex:
                                                                temp['return'] = False
                                                                temp['code'] = 404
                                                                temp['message'] = str(ex)
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                                            
                                                            else:
                                                                if(len(user_credential_ref) < 1):
                                                                    temp['return'] = False
                                                                    temp['code'] = 114
                                                                    temp['message'] = "Invalid USER id."
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()
                                                                
                                                                else:
                                                                    user_credential_ref = user_credential_ref[0]

                                                                    if(user_credential_ref.user_profile_id in (None, "")):
                                                                        temp['return'] = False
                                                                        temp['code'] = 106
                                                                        temp['message'] = "USER PROFILE does not exist."
                                                                        data_returned['data'][id] = temp.copy()
                                                                        temp.clear()
                                                                    
                                                                    else:

                                                                        if(self_user_profile_ref.user_profile_id == user_credential_ref.user_profile_id.user_profile_id):
                                                                            temp['message'] = "self profile delete"

                                                                        else:
                                                                            pass
                                                                        
                                                                        if(user_credential_ref.user_profile_id.user_profile_pic in (None, "")):
                                                                            pass
                                                                        else:
                                                                            fs = FileSystemStorage()
                                                                            fs.delete(user_credential_ref.user_profile_id.user_profile_pic.image_name)
                                                                            user_credential_ref.user_profile_id.user_profile_pic.delete()
                                                                        
                                                                        user_credential_ref.user_profile_id.delete()
                                                                        
                                                                        temp['return'] = True
                                                                        temp['code'] = 100
                                                                        data_returned['data'][id] = temp.copy()
                                                                        temp.clear()
                                                                    

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

                        elif(incoming_data["action"].upper() == "EDIT"):
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
                                                    data_returned['message'] = "EDIT without IMAGE."

                                                else:
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 405
                                                    data_returned['message'] = user_profile_de_serialized.errors
                                                    return JsonResponse(data_returned, safe=True)

                                    return JsonResponse(data_returned, safe=True)
                        
                        elif(incoming_data["action"].upper() == "READ"):
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
                                    data = auth.check_authorization("user")

                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 102
                                        data_returned['message'] = "Invalid HASH."
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        self_user_profile_ref = User_Credential.objects.get(user_credential_id = int(data[1])).user_profile_id
                                        
                                        if('user_id' in incoming_data.keys()): # user fetching other user_profiles
                                            data_returned['data'] = dict()
                                            temp = dict()

                                            user_ids = tuple(set(incoming_data['user_id']))
                                            if(len(user_ids) < 1):
                                                data_returned['return'] = False
                                                data_returned['code'] = 404
                                                data_returned['message'] = "Value Error : Atleast one user id required."
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                if(0 in user_ids): # all at once
                                                    user_profile_ref = User_Profile.objects.all()
                                                        
                                                    if(len(user_profile_ref) < 1):
                                                        temp['return'] = False
                                                        temp['code'] = 404
                                                        temp['message'] = "Already empty tray of USER PROFILES."
                                                        data_returned['data'][0] = temp.copy()
                                                        temp.clear()
                                                        return JsonResponse(data_returned, safe=True)
                                                        
                                                    else:
                                                        user_profile_serialized = User_Profile_Serializer(user_profile_ref, many=True).data

                                                        temp['return'] = True
                                                        temp['code'] = 100
                                                        temp['data'] = list()
                                                        
                                                        for user in user_profile_serialized:
                                                            if(user['user_profile_id'] == self_user_profile_ref.user_profile_id):
                                                                key = "self"
                                                            else:
                                                                key = int(user['user_profile_id'])

                                                            if(user['user_profile_pic'] in (None, "")):
                                                                user['user_profile_pic'] = None
                                                            else:
                                                                user['user_profile_pic'] = Image.objects.get(image_id = int(user['user_profile_pic'])).image_url

                                                            temp['data'].append({key : user})
                                                        
                                                        data_returned['data'][0] = temp.copy()
                                                        temp.clear()

                                                else: # individual id_profile fetch
                                                    for id in user_ids:
                                                        try:
                                                            user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                                            
                                                        except Exception as ex:
                                                            temp['return'] = False
                                                            temp['code'] = 404
                                                            temp['message'] = str(ex)
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()

                                                        else:
                                                            if(len(user_credential_ref) < 1):
                                                                temp['return'] = False
                                                                temp['code'] = 114
                                                                temp['message'] = "Invalid USER id."
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                                                
                                                            else:
                                                                user_credential_ref = user_credential_ref[0]

                                                                if(user_credential_ref.user_profile_id in (None, "")):
                                                                    temp['return'] = False
                                                                    temp['code'] = 106
                                                                    temp['message'] = "USER PROFILE does not exist."
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()

                                                                else:
                                                                    user_profile_serialized = User_Profile_Serializer(user_credential_ref.user_profile_id, many=False).data

                                                                    # if(self_user_profile_ref.user_profile_id == user_profile_serialized['user_profile_id']):
                                                                    #     key = "self"
                                                                    # else:
                                                                    #     key = int(user_profile_serialized['user_profile_id'])

                                                                    temp['return'] = True
                                                                    temp['code'] = 100

                                                                    if(user_profile_serialized['user_profile_pic'] in (None, "")):
                                                                        pass
                                                                    else:
                                                                        user_profile_serialized['user_profile_pic'] = Image.objects.get(image_id = int(user_profile_serialized['user_profile_pic']))

                                                                    temp['data'] = user_profile_serialized
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()
                                        
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
                                                
                                                if(user_profile_serialized['user_profile_pic'] in (None, "")):
                                                    pass
                                                else:
                                                    user_profile_serialized['user_profile_pic'] = Image.objects.get(image_id = int(user_profile_serialized['user_profile_pic']))
                                                
                                                data_returned['data'] = user_profile_serialized

                                    return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "Parent action invalid"
        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def admin_credential_API(request):
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
                        if(incoming_data["action"].upper() == "CREATE"):
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
                                data = auth.check_authorization("admin", "prime") #only prime admins can grant admin access
        
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 110
                                    data_returned['message'] = "USER might not have ADMIN PRIME privileges."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    if('user_id' in incoming_data.keys()): # only this method of admin inclusion accepted
                                        data_returned['return'] = list()
                                        data_returned['code'] = list()
                                        data_returned['message'] = list()
                                        data_returned['data'] = list()

                                        for id in incoming_data['user_id']:
                                            try:
                                                if(int(data[1]) == int(id)):
                                                    data_returned['return'].append(False)
                                                    data_returned['code'].append(112)
                                                    data_returned['message'].append("USER already ADMIN")
                                                    data_returned['data'].append("self")
                                        
                                                else:
                                                    user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))

                                                    if(len(user_credential_ref) < 1):
                                                        data_returned['return'].append(False)
                                                        data_returned['code'].append(114)
                                                        data_returned['message'].append("USER ID not exist")
                                                        data_returned['data'].append(None)

                                                    else:
                                                        try:
                                                            user_credential_ref = user_credential_ref[0]
                                                            admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(user_credential_ref.user_credential_id))

                                                        except Exception as ex:
                                                            data_returned['return'].append(False)
                                                            data_returned['code'].append(404)
                                                            data_returned['message'].append(str(ex))
                                                            data_returned['data'].append(None)
                                    
                                                        else:
                                                            if(len(admin_credential_ref) > 0):
                                                                data_returned['return'].append(False)
                                                                data_returned['code'].append(112)
                                                                data_returned['message'].append("USER already ADMIN")
                                                                data_returned['data'].append(id)
                                        
                                                            else:
                                                                admin_credential_ref_new = Admin_Credential(user_credential_id = user_credential_ref)
                                                                admin_credential_ref_new.save()

                                                                data_returned['return'].append(True)
                                                                data_returned['code'].append(100)
                                                                data_returned['message'].append("Admin Privileges Granted.")
                                                                data_returned['data'].append(id)

                                            except Exception as ex:
                                                data_returned['return'].append(False)
                                                data_returned['code'].append(404)
                                                data_returned['message'].append(str(ex))
                                                data_returned['data'].append(None)
                            
                                    else:
                                        data_returned['return'] = False
                                        data_returned['code'] = 402
                                        data_returned['message'] = "user_id field required."
                                        return JsonResponse(data_returned, safe=True)

                                return JsonResponse(data_returned, safe=True)
                        
                        elif(incoming_data["action"].upper() == "DELETE"):
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
                                if('user_id' in incoming_data.keys()): # admin prime revoking others access
                                    data = auth.check_authorization("admin", "prime") #only prime admins can revoke admin access from others
                
                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 110
                                        data_returned['message'] = "USER might not have ADMIN PRIME privileges."
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        user_ids = tuple(set(incoming_data['user_id']))

                                        if(len(user_ids) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = "Value Error : Atleast one user id required."
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            if(0 in user_ids):
                                                data_returned['data'] = dict()
                                                temp = dict()

                                                admin_credential_ref_all = Admin_Credential.objects.all().exclude(user_credential_id = int(data[1]))

                                                if(len(admin_credential_ref_all) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 404
                                                    temp['message'] = "Already ADMIN Tray is empty."
                                                    data_returned['data'][0] = temp.copy()
                                                    temp.clear()
                                                    return JsonResponse(data_returned, safe=True)
                                                
                                                else:
                                                    admin_credential_ref_all.delete()

                                                    temp['return'] = True
                                                    temp['code'] = 100
                                                    temp['message'] = "ADMIN(-1) Tray cleared."
                                                    temp['data'][0] = temp.copy()
                                                    temp.clear()
                                            
                                            else:
                                                data_returned['data'] = dict()
                                                temp = dict()

                                                for id in user_ids: # self delete not allowed this way SECURITY CHECK
                                                    try:
                                                        if(int(data[1]) == int(id)):
                                                            temp['return'] = False
                                                            temp['code'] = 404
                                                            temp['message'] = "Operation Error : Self delete not allowed."
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()
                                                        
                                                        else:
                                                            user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))

                                                            if(len(user_credential_ref) < 1):
                                                                temp['return'] = False
                                                                temp['code'] = 114
                                                                temp['message'] = "INVALID : USER ID."
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                                
                                                            else:
                                                                try:
                                                                    user_credential_ref = user_credential_ref[0]
                                                                    admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(user_credential_ref.user_credential_id))
                                
                                                                except Exception as ex:
                                                                    temp['return'] = False
                                                                    temp['code'] = 404
                                                                    temp['message'] = str(ex)
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()
                                                    
                                                                else:
                                                                    if(len(admin_credential_ref) < 1):
                                                                        temp['return'] = False
                                                                        temp['code'] = 113
                                                                        temp['message'] = "USER not ADMIN"
                                                                        data_returned['data'][id] = temp.copy()
                                                                        temp.clear()
                                                        
                                                                    else:
                                                                        admin_credential_ref = admin_credential_ref[0]
                                                                        admin_credential_ref.delete()

                                                                        temp['return'] = True
                                                                        temp['code'] = 100
                                                                        temp['message'] = "Admin Privileged Revoked."
                                                                        data_returned['data'][id] = temp.copy()
                                                                        temp.clear()

                                                    except Exception as ex:
                                                        temp['return'] = False
                                                        temp['code'] = 404
                                                        temp['message'] = str(ex)
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                    
                                else: # self delete
                                    data = auth.check_authorization("admin")
                                    
                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 114
                                        data_returned['message'] = "USER NOT ADMIN."
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1]))
                                        admin_credential_ref.delete()

                                        data_returned['return'] = True
                                        data_returned['code'] = 100

                                return JsonResponse(data_returned, safe=True)
                        
                        elif(incoming_data["action"].upper() == "EDIT"):
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
                                data = auth.check_authorization("admin", "prime") #admins can change other admins and self change is permitted
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 110
                                    data_returned['message'] = "USER not ADMIN PRIME."
                                    return JsonResponse(data_returned, safe=True)

                                else:
                                    if("updates" in incoming_data.keys()): # admin prime change others, ONLY THIS METHOD ALLOWED

                                        if(len(incoming_data['updates']) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = "No updates provided."
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            self_admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1]))
                                            data_returned['data'] = dict()
                                            temp = dict()

                                            updates = tuple(incoming_data['updates'])
                                            
                                            for update in updates:
                                                try:
                                                    admin_credential_ref = Admin_Credential.objects.filter(admin_credential_id = int(update['admin_id']))
                                                    key = f"{update['admin_id']}_{update['privilege_id']}"

                                                except Exception as ex:
                                                    temp['return'] = False
                                                    temp['code'] = 404
                                                    temp['message'] = str(ex)
                                                    data_returned['data'][key] = temp.copy()
                                                    temp.clear()
                                                
                                                else:
                                                    if(len(admin_credential_ref) < 1):
                                                        temp['return'] = False
                                                        temp['code'] = 111
                                                        temp['message'] = "Invalid ADMIN CRED id."
                                                        data_returned['data'][key] = temp.copy()
                                                        temp.clear()
                                                    
                                                    else:
                                                        admin_credential_ref = admin_credential_ref[0]
                                                        # if(int(admin_credential_ref.admin_credential_id) == int(self_admin_credential_ref.admin_credential_id)):
                                                        #     key = "self"
                                                        # else:
                                                        #     key = int(admin_credential_ref.admin_credential_id)
                                                
                                                        try:
                                                            if(int(update['privilege_id']) < 0):
                                                                flag = False # delete pair
                                                                update['privilege_id'] = int(update['privilege_id'])*(-1)
                                                            else:
                                                                flag = True # create pair
                                                            admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(update['privilege_id']))
                                                    
                                                        except Exception as ex:
                                                            temp['return'] = False
                                                            temp['code'] = 404
                                                            temp['message'] = str(ex)
                                                            data_returned['data'][key] = temp.copy()
                                                            temp.clear()
                                                    
                                                        else:
                                                            if(len(admin_privilege_ref) < 1):
                                                                temp['return'] = False
                                                                temp['code'] = 116
                                                                temp['message'] = "Invalid ADMIN PRIV id."
                                                                data_returned['data'][key] = temp.copy()
                                                                temp.clear()
                                                    
                                                            else:
                                                                admin_privilege_ref = admin_privilege_ref[0]
                                                                many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id, 
                                                                                                                            admin_privilege_id = admin_privilege_ref.admin_privilege_id)
                                                                
                                                                if(flag == True):
                                                                    if(len(many_to_many_ref) > 0):
                                                                        temp['return'] = False
                                                                        temp['code'] = 115
                                                                        temp['message'] = "ADMIN CRED <-> ADMIN PRIV pair exists."
                                                                        data_returned['data'][key] = temp.copy()
                                                                        temp.clear()
                                                                
                                                                    else:
                                                                        many_to_many_new = Admin_Cred_Admin_Prev_Int(admin_credential_id = admin_credential_ref,
                                                                                                                    admin_privilege_id = admin_privilege_ref)
                                                                        many_to_many_new.save()

                                                                        temp['return'] = True
                                                                        temp['code'] = 100
                                                                        temp['message'] = "ADMIN CRED <-> ADMIN PRIV pair generated."
                                                                        data_returned['data'][key] = temp.copy()
                                                                        temp.clear()
                                                                
                                                                else:
                                                                    if(len(many_to_many_ref) < 1):
                                                                        temp['return'] = False
                                                                        temp['code'] = 115
                                                                        temp['message'] = "ADMIN CRED <-> ADMIN PRIV does not exist."
                                                                        data_returned['data'][key] = temp.copy()
                                                                        temp.clear()
                                                                
                                                                    else:
                                                                        many_to_many_ref = many_to_many_ref[0]
                                                                        many_to_many_ref.delete()

                                                                        temp['return'] = True
                                                                        temp['code'] = 100
                                                                        temp['message'] = "ADMIN CRED <-> ADMIN PRIV pair removed."
                                                                        data_returned['data'][f"{update['admin_id']}_{update['privilege_id']}"] = temp.copy()
                                                                        temp.clear()

                                    else:
                                        data_returned['return'] = False
                                        data_returned['code'] = 402
                                        data_returned['message'] = "key error : [updates]"

                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
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
                                if('user_id' in incoming_data.keys()): # admin prime fetching others admin details
                                    data = auth.check_authorization("admin", "prime") #only prime admins can fetch admin access from others
                
                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 110
                                        data_returned['message'] = "USER might not have ADMIN PRIME privileges."
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        user_ids = tuple(incoming_data['user_id'])

                                        if(len(user_ids) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = "Value Error : Atleast one user id required."
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            data_returned['data'] = dict()
                                            temp = dict()

                                            if(0 in user_ids):
                                                admin_credential_ref_all = Admin_Credential.objects.all()

                                                if(len(admin_credential_ref_all) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 404
                                                    temp['message'] = "ADMIN Tray is empty."
                                                    data_returned['data'][0] = temp.copy()
                                                    temp.clear()
                                                    return JsonResponse(data_returned, safe=True)
                                                
                                                else:
                                                    admin_credential_all_serialized = Admin_Credential_Serializer(admin_credential_ref_all, many=True).data

                                                    temp['return'] = True
                                                    temp['code'] = 100
                                                    data_returned['data'][0] = temp.copy()
                                                    temp.clear()

                                                    for admin in admin_credential_all_serialized:
                                                        if(admin['user_credential_id'] == int(data[1])):
                                                            key = "self"
                                                        else:
                                                            key = admin['user_credential_id']                                            

                                                        many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin['admin_credential_id'])
                                                        if(len(many_to_many_ref) < 1):
                                                            privileges = None
                                                        else:
                                                            privileges = list()
                                                            for mtmr in many_to_many_ref:
                                                                privileges.append(mtmr.admin_privilege_id.admin_privilege_id)

                                                        
                                                        temp['admin'] = admin
                                                        temp["privilege"] = privileges
                                                        data_returned['data'][0][admin['user_credential_id']] = temp.copy()
                                                        temp.clear()
                                            
                                            else:
                                                data_returned['data'] = dict()
                                                temp = dict()
                                                
                                                for id in user_ids: # self fetch allowed this way SECURITY CHECK
                                                    try:
                                                        user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))

                                                        if(len(user_credential_ref) < 1):
                                                            temp['return'] = False
                                                            temp['code'] = 114
                                                            temp['message'] = "USER ID not exist"
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()
                                                
                                                        else:
                                                            try:
                                                                user_credential_ref = user_credential_ref[0]
                                                                admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(user_credential_ref.user_credential_id))
                                
                                                            except Exception as ex:
                                                                temp['return'] = False
                                                                temp['code'] = 404
                                                                temp['message'] = str(ex)
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                                    
                                                            else:
                                                                if(len(admin_credential_ref) < 1):
                                                                    temp['return'] = False
                                                                    temp['code'] = 113
                                                                    temp['message'] = "USER not ADMIN"
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()
                                                        
                                                                else:
                                                                    admin_credential_ref = admin_credential_ref[0]
                                                                    admin_credential_serialized = Admin_Credential_Serializer(admin_credential_ref, many=False).data

                                                                    if(admin_credential_serialized['user_credential_id'] == int(data[1])):
                                                                        key = "self"
                                                                    else:
                                                                        key = admin_credential_serialized['user_credential_id']

                                                                    many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_serialized['admin_credential_id'])
                                                                    if(len(many_to_many_ref) < 1):
                                                                        privileges = None
                                                                    else:
                                                                        privileges = list()
                                                                        for mtmr in many_to_many_ref:
                                                                            privileges.append(mtmr.admin_privilege_id.admin_privilege_id)
                                                                    
                                                                    temp['data'] = dict()
                                                                    temp['data']['admin'] = admin_credential_serialized
                                                                    temp['data']['privilege'] = privileges

                                                                    temp['return'] = True
                                                                    temp['code'] = 100
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()

                                                    except Exception as ex:
                                                        temp['return'] = False
                                                        temp['code'] = 404
                                                        temp['message'] = str(ex)
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                    
                                else: # self fetch
                                    data = auth.check_authorization("admin")
                                    
                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 114
                                        data_returned['message'] = "USER NOT ADMIN."
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1]))
                                        admin_credential_serialized = Admin_Credential_Serializer(admin_credential_ref, many=False).data
                                        
                                        key = "self"
                                        temp = {key : admin_credential_serialized}

                                        many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = temp[key]['admin_credential_id'])
                                        if(len(many_to_many_ref) < 1):
                                            privileges = None
                                        else:
                                            privileges = list()
                                        for mtmr in many_to_many_ref:
                                            privileges.append(mtmr.admin_privilege_id.admin_privilege_id)
                                        
                                        temp['privilege_id'] = privileges

                                        data_returned['return'] = True
                                        data_returned['code'] = 100
                                        data_returned['data'] = temp

                                return JsonResponse(data_returned, safe=True)
                        
                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "Parent action invalid"
        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def admin_privilege_API(request):
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
                        if(incoming_data["action"].upper() == "CREATE"):
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
                                data = auth.check_authorization("admin", "prime") #only prime admins can create admin priv
                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 110
                                    data_returned['message'] = "USER might not have ADMIN PRIME privileges."
                                    return JsonResponse(data_returned, safe=True)
                                else:
                                    try:
                                        incoming_data = incoming_data['data']
                                        admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = incoming_data["admin_privilege_name"].upper())
                                    
                                    except Exception as ex:
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = str(ex)
                                        return JsonResponse(data_returned, safe=True)

                                    else:
                                        if(len(admin_privilege_ref) > 0):
                                            data_returned['return'] = False
                                            data_returned['code'] = 117
                                            data_returned['message'] = 'Admin Privilege Exists.'
                                            return JsonResponse(data_returned, safe=True)

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
                
                                    return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                privilege_ids = tuple(set(incoming_data['privilege_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 404
                                data_returned['message'] = str(ex)
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("admin", "prime") #only prime admins can grant admin access
                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 110
                                    data_returned['message'] = "USER might not have ADMIN PRIME privileges."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    try:
                                        if(len(privilege_ids) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 403
                                            data_returned['message'] = "At least one id required to operate."
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            data_returned['data'] = dict()
                                            temp = dict()

                                            if(0 in privilege_ids):
                                                temp['return'] = False
                                                temp['code'] = 404
                                                temp['message'] = "0 -> universal deletion not applicable."
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                for id in privilege_ids:
                                                    try:
                                                        admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(id))
                                                    
                                                    except Exception as ex:
                                                        temp['return'] = False
                                                        temp['code'] = 404
                                                        temp['message'] = str(ex)
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                                    
                                                    else:
                                                        if(len(admin_privilege_ref) < 1):
                                                            temp['return'] = False
                                                            temp['code'] = 116
                                                            temp['message'] = "Privilege does not exist."
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()
                                                        
                                                        else:
                                                            admin_privilege_ref = admin_privilege_ref[0]
                                                            admin_privilege_ref.delete()

                                                            temp['return'] = True
                                                            temp['code'] = 100
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()

                                    
                                    except Exception as ex:
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = str(ex)
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                privilege_ids = tuple(set(incoming_data['privilege_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 404
                                data_returned['message'] = str(ex)
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("admin") #only prime admins can grant admin access
                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 111
                                    data_returned['message'] = "USER might not have ADMIN privileges."
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    if(len(privilege_ids) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 403
                                        data_returned['message'] = "Atleast one Privilege ID required."
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        data_returned['data'] = dict()
                                        temp = dict()

                                        if(0 in privilege_ids):
                                            admin_privilege_ref = Admin_Privilege.objects.all()

                                            if(len(admin_privilege_ref) < 1):
                                                temp['return'] = False
                                                temp['code'] = 404
                                                temp['message'] = "Admin Privilege Tray empty."
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                admin_privilege_serialized = Admin_Privilege_Serializer(admin_privilege_ref, many=True)
                                                
                                                temp['return'] = True
                                                temp['code'] = 100
                                                temp['data'] = admin_privilege_serialized.data
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()
                                        
                                        else:
                                            for id in privilege_ids:
                                                try:
                                                    admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(id))
                                                
                                                except Exception as ex:
                                                    temp['return'] = False
                                                    temp['code'] = 404
                                                    temp['message'] = str(ex)
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()
                                                
                                                else:
                                                    if(len(admin_privilege_ref) < 1):
                                                        temp['return'] = False
                                                        temp['code'] = 116
                                                        temp['message'] = "Invalid PRIVILEGE ID."
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                            
                                                    else:
                                                        admin_privilege_ref = admin_privilege_ref[0]
                                                        admin_privilege_serialized = Admin_Privilege_Serializer(admin_privilege_ref, many=False)

                                                        temp['return'] = True
                                                        temp['code'] = 100
                                                        temp['data'] = admin_privilege_serialized.data
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()

                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = str(ex)
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "Parent action invalid"
        return JsonResponse(data_returned, safe=True)

# ------------------------------VIEW_SPACE-------------------------------------

pinned = [
    '<span style="color: yellow;">[25-02-2021]</span> All methods migrated to POST -> check postman export for clarity',
    '<span style="color: yellow;">[23-02-2021]</span> FETCH method have been changed to REQUEST method',
]

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
            data_returned['pinned'] = pinned
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

        