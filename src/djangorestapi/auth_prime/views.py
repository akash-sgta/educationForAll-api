from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from auth_prime.models import User_Credential, Admin_Privilege, Admin_Credential, Token_Table, User_Profile, Admin_Cred_Admin_Prev_Int
from auth_prime.serializer import User_Credential_Serializer, Admin_Privilege_Serializer, Admin_Credential_Serializer, Token_Table_Serializer, User_Profile_Serializer

from auth_prime.authorize import Authorize, Cookie

# Create your views here.

auth = Authorize()
API_PRIVATE_KEY = "ugabuga"
API_VERSION = '1.0'
# -------------------------------API_SPACE-------------------------------------

@csrf_exempt
def user_credential_API(request):
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
            incoming_action = user_data["action"]
            incoming_api_version = user_data["api_v"]
            incoming_data = user_data["data"]
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

        if(incoming_action == "signup"):
            data_returned['action'] += "-"+incoming_action.upper()
            auth.clear()

            try:
                user_credential_de_serialized = User_Credential_Serializer(data = incoming_data)
            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 404
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            data_to_check = user_credential_de_serialized.initial_data
            data_to_check['user_email'] = (data_to_check['user_email']).lower()
            user_credential_ref = User_Credential.objects.filter(user_email=data_to_check['user_email'])

            if(len(user_credential_ref) > 0):
                data_returned['return'] = False
                data_returned['code'] = 104
            else:
                try:
                    auth.user_email = data_to_check['user_email'].lower()
                    auth.user_password = data_to_check['user_password']
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = str(ex)

                    return JsonResponse(data_returned, safe=True)
                
                data = auth.create_password_hashed()
                
                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = data[1]
                else:
                    user_credential_de_serialized.initial_data['user_password'] = data[1] # successfully hashed password
                    
                if(user_credential_de_serialized.is_valid()):
                    user_credential_de_serialized.save()

                    data = auth.sanction_authorization()
                    
                    if(data[0] == False):
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = data[1]
                    else:
                        data_returned['return'] = True
                        data_returned['code'] = 100
                        data_returned['data'] = {'hash' : data[1]}
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 405
                    data_returned['message'] = user_credential_de_serialized.errors
                
            return JsonResponse(data_returned, safe=True)

        elif(incoming_action in ("signin","login")):
            data_returned['action'] += "-"+incoming_action.upper()
            auth.clear()

            try:
                auth.user_email = incoming_data['user_email'].lower()
                auth.user_password = incoming_data['user_password']
            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 404
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            data = auth.sanction_authorization()
            
            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 404
                data_returned['message'] = data[1]
            else:
                data_returned['return'] = True
                data_returned['code'] = 100
                data_returned['data'] = {'hash' : data[1]}

            return JsonResponse(data_returned, safe=True)

        elif(incoming_action in ("signout","logout")):
            data_returned['action'] += "-"+incoming_action.upper()
            auth.clear()

            try:
                auth.token = incoming_data['hash']
            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 404
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            data = auth.check_authorization("user")

            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 102
            else:
                token_table_ref = Token_Table.objects.filter(user_credential_id = int(data[1]))
                token_table_ref = token_table_ref[0]
                token_table_ref.delete()

                data_returned['return'] = True
                data_returned['code'] = 100
            
            return JsonResponse(data_returned, safe=True)

        else:
            data_returned['return'] = False
            data_returned['code'] = 403
        
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
            incoming_data = user_data["data"]
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
            auth.token = incoming_data["hash"]
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
            
            
        data = auth.check_authorization("user")
            
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102            
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
            
            
        data = auth.check_authorization("user")            
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))            
            user_credential_de_serialized = User_Credential_Serializer(user_credential_ref,
                                                                       data = incoming_data)
            
            if("user_email" in user_credential_de_serialized.initial_data.keys()):
                email_temp = user_credential_de_serialized.initial_data['user_email'].lower()

                user_credential_ref_temp = User_Credential.objects.filter(user_email = email_temp)

                if(len(user_credential_ref_temp) > 0):
                    user_credential_ref_temp = user_credential_ref_temp[0]
                    if(user_credential_ref_temp.user_credential_id != user_credential_ref.user_credential_id):
                        data_returned['return'] = False
                        data_returned['code'] = 104
            
                        flag = False # user email exists but not belong to hash user
                    else:
                        flag = True
                else:
                    flag = True
            else:
                email_temp = user_credential_ref.user_email.lower()
                flag = True
            
                
            if(flag == True):
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

        data = auth.check_authorization("user")

        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                    
            data_returned['return'] = True
            data_returned['code'] = 100
            data_returned['data'] = User_Credential_Serializer(user_credential_ref, many=False).data
                    
            # initially not handed to user for security purposes
            del(data_returned['data']['user_password'])
            del(data_returned['data']["user_security_question"])
            del(data_returned['data']["user_security_answer"])
            
        return JsonResponse(data_returned, safe=True)
    
    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def user_profile_API(request):
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

        data = auth.check_authorization("user")
        
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

            print(user_credential_ref)
            print(user_credential_ref.user_profile_id)
            if(user_credential_ref.user_profile_id in (None, "")):

                try:
                    user_profile_de_serialized = User_Profile_Serializer(data = incoming_data)
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = str(ex)

                    return JsonResponse(data_returned, safe=True)

                if("prime" in user_profile_de_serialized.initial_data.keys()):
                    if(user_profile_de_serialized.initial_data["prime"] == True): # if student then roll number required
                        if("user_roll_number" in user_profile_de_serialized.initial_data.keys()):
                            if(user_profile_de_serialized.initial_data["user_roll_number"] in (None, "")):
                                flag = False
                            else:
                                flag = True
                        else:
                            flag = False
                    else:
                        flag = True
                else:
                    flag = True
                
                if(flag == False):
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = "student profile requires university roll number."

                    return JsonResponse(data_returned, safe=True)
                else:
                    pass


                
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
            
            else:
                data_returned['return'] = False
                data_returned['code'] = 105

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
            
            
        data = auth.check_authorization("user")
            
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

            if(user_credential_ref.user_profile_id == None):
                data_returned['return'] = False
                data_returned['code'] = 106
            else:
                user_credential_ref.user_profile_id.delete()
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

        data = auth.check_authorization("user")
        
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

            if(user_credential_ref.user_profile_id == None):
                data_returned['return'] = False
                data_returned['code'] = 106
            
            else:
                try:
                    user_profile_de_serialized = User_Profile_Serializer(user_credential_ref.user_profile_id, data = incoming_data)
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = str(ex)

                    return JsonResponse(data_returned, safe=True)
                
                if("prime" in user_profile_de_serialized.initial_data.keys()):
                    if(user_profile_de_serialized.initial_data["prime"] == True): # if student then roll number required
                        if("user_roll_number" in user_profile_de_serialized.initial_data.keys()):
                            if(user_profile_de_serialized.initial_data["user_roll_number"] in (None, "")):
                                flag = False
                            else:
                                flag = True
                        else:
                            flag = False
                    else:
                        flag = True
                else:
                    flag = True
                
                if(flag == False):
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = "student profile requires university roll number."

                    return JsonResponse(data_returned, safe=True)
                else:
                    pass
                
                user_profile_de_serialized.initial_data["user_profile_id"] = user_credential_ref.user_profile_id.user_profile_id
                if(user_profile_de_serialized.is_valid()):
                    user_profile_de_serialized.save()

                    data_returned['return'] = True
                    data_returned['code'] = 100
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 405
                    data_returned['message'] = user_profile_de_serialized.errors

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

        data = auth.check_authorization("user")
        
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            data_returned['return'] = True
            data_returned['code'] = 100

            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
            if(user_credential_ref.user_profile_id == None):
                data_returned['data'] = "No Profile found"
            else:
                user_profile_serialized = User_Profile_Serializer(user_credential_ref.user_profile_id, many=False)
                data_returned['data'] = user_profile_serialized.data

        return JsonResponse(data_returned, safe=True)    

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def admin_API(request):
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

def admin_VIEW(request):
    global auth
    data_returned = dict()

    data_returned['site_name'] = 'TABLE'

    return render(request, 'auth_prime/templates/admin.html', data_returned)

def admin_privilege_VIEW(request):
    global auth
    data_returned = dict()

    data_returned['site_name'] = 'PRIVILEGES'

    return render(request, 'auth_prime/templates/admin.html', data_returned)