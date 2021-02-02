from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from auth_prime.models import User_Credential, Admin_Privilege, Admin_Credential, Token_Table
from auth_prime.serializer import User_Credential_Serializer, Admin_Privilege_Serializer, Admin_Credential_Serializer, Token_Table_Serializer

from auth_prime.authorize import Authorize

# Create your views here.

auth = Authorize()

@csrf_exempt
def user_API(request, id=0):
    global auth
    data_returned = dict()

    if(request.method == 'FETCH'):

        data_returned['action'] = "FETCH"

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        try:
            incoming_action = user_data["action"]
            incoming_data = user_data["data"]
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        if(incoming_action == 'get_one'):

            data_returned['action'] += '-GET_ONE'
            
            auth.clear()

            try:
                auth.token = incoming_data['hash']
            except Exception as ex:
                
                data_returned['return'] = False
                data_returned['code'] = 502
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            data = auth.is_authorized()

            if(data[0] == True):
                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(data[1]))
                if(len(user_credential_ref) < 1):

                    data_returned['return'] = False
                    data_returned['code'] = 401
                    
                else:
                    user_credential_ref = user_credential_ref[0]
                    
                    data_returned['return'] = True
                    data_returned['code'] = 200
                    data_returned['data'] = User_Credential_Serializer(user_credential_ref, many=False).data
                    
                    # initially not handed to user for security purposes
                    del(data_returned['data']['user_password'])
                    del(data_returned['data']['user_credential_id'])
                    del(data_returned['data']["user_security_question"])
                    del(data_returned['data']["user_security_answer"])

            else:

                data_returned['return'] = False
                data_returned['code'] = 501
                data_returned['message'] = data[1]
        
        elif(incoming_action == 'get_all'):

            data_returned['action'] += '-GET_ALL'

            auth.clear()
            auth.token = incoming_data['hash']

            data = auth.is_authorized_admin()

            if(data[0] == False):

                data_returned['return'] = False
                data_returned['code'] = 501
                data_returned['message'] = data[1]
            
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
                    del(data_returned['data'][i]["user_security_question"])
                    del(data_returned['data'][i]["user_security_answer"])
                    
                    i += 1
        
        else:

            data_returned['return'] = False
            data_returned['code'] = 402
        
        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'POST'):
        
        data_returned['action'] = "POST"

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_action = user_data["action"]
            incoming_data = user_data["data"]
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        if(incoming_action == "signup"):

            data_returned['action'] += "-SIGNUP"

            try:
                user_credential_de_serialized = User_Credential_Serializer(data = incoming_data)
            except Exception as ex:
                
                data_returned['return'] = False
                data_returned['code'] = 502
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            data_to_check = user_credential_de_serialized.initial_data
            data_to_check['user_email'] = (data_to_check['user_email']).lower()
            user_credential_ref = User_Credential.objects.filter(user_email=data_to_check['user_email'])

            if(len(user_credential_ref) > 0):

                data_returned['return'] = False
                data_returned['code'] = 403
            
            else:
                
                auth.clear()
                
                try:
                    auth.user_email = data_to_check['user_email'].lower()
                except Exception as ex:
                    
                    data_returned['return'] = False
                    data_returned['code'] = 501
                    data_returned['message'] = str(ex)

                    return JsonResponse(data_returned, safe=True)
                
                auth.user_password = data_to_check['user_password']
                
                data = auth.create_password_hashed()
                
                if(data[0] == False):
                    
                    data_returned['return'] = False
                    data_returned['code'] = 501
                    data_returned['message'] = data[1]

                else:
                    user_credential_de_serialized.initial_data['user_password'] = data[1] # successfully hashed password
                    
                if(user_credential_de_serialized.is_valid()):

                    user_credential_de_serialized.save()

                    data = auth.sanction_authorization()

                    if(data[0] == False):
                        
                        data_returned['return'] = False
                        data_returned['code'] = 501
                        data_returned['message'] = data[1]

                    else:
                        
                        data_returned['return'] = True
                        data_returned['code'] = 200
                        data_returned['data'] = dict()
                        data_returned['data']['hash'] = data[1]
                
                else:

                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = user_credential_de_serialized.errors

        elif(incoming_action == "login"):

            data_returned['action'] += "-LOGIN"

            auth.clear()
            try:
                auth.user_email = incoming_data['user_email'].lower()
            except Exception as ex:

                data_returned['return'] = False
                data_returned['code'] = 501
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            try:
                auth.user_password = incoming_data['user_password']
            except Exception as ex:
                
                data_returned['return'] = False
                data_returned['code'] = 502
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            data = auth.sanction_authorization()
            
            if(data[0] == False):
                
                data_returned['return'] = False
                data_returned['code'] = 501
                data_returned['message'] = data[1]

            else:

                data_returned['return'] = True
                data_returned['code'] = 200
                data_returned['data'] = dict()
                data_returned['data']['hash'] = data[1]

        else:

            data_returned['return'] = False
            data_returned['code'] = 402
        
        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'PUT'):

        data_returned['action'] = "PUT"

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_action = user_data["action"]
            incoming_data = user_data["data"]
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        if(incoming_action == 'user'):
            
            data_returned['action'] += "-USER"

            auth.clear()
            try:
                auth.token = incoming_data['hash']
            except Exception as ex:
                
                data_returned['return'] = False
                data_returned['code'] = 502
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)
            
            
            data = auth.is_authorized()
            
            if(data[0] == False):

                data_returned['return'] = False
                data_returned['code'] = 501
                data_returned['message'] = data[1]

            else:
                
                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(data[1]))
                user_credential_ref = user_credential_ref[0]
                user_credential_de_serialized = User_Credential_Serializer(user_credential_ref, data=incoming_data['data'])

                user_credential_ref_temp = User_Credential.objects.filter(user_email=user_credential_de_serialized.initial_data['user_email'].lower())

                if(len(user_credential_ref_temp) > 0):

                    user_credential_ref_temp = user_credential_ref_temp[0]
                    
                    if(user_credential_ref_temp.user_credential_id != user_credential_ref.user_credential_id): # True if : uid through email != uid through hash

                        data_returned['return'] = False
                        data_returned['code'] = 403
                        
                        flag = False

                    else:

                        flag = True
                    
                else:

                    flag = True
                
                if(flag == True):

                    user_credential_de_serialized.initial_data['user_email'] = user_credential_de_serialized.initial_data['user_email'].lower()
                    
                    # necessary fields for serializer but can not be given permission to user
                    user_credential_de_serialized.initial_data['user_password'] = user_credential_ref.user_password
                    user_credential_de_serialized.initial_data['user_security_question'] = user_credential_ref.user_security_question
                    user_credential_de_serialized.initial_data['user_security_answer'] = user_credential_ref.user_security_answer

                    if(user_credential_de_serialized.is_valid()):
                        user_credential_de_serialized.save()

                        data_returned['return'] = True
                        data_returned['code'] = 200

                    else:
                        
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = user_credential_de_serialized.errors
        
        else:

            data_returned['return'] = False
            data_returned['code'] = 402
            
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'DELETE'):

        data_returned['action'] = "DELETE"

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        try:
            incoming_action = user_data["action"]
            incoming_data = user_data["data"]
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        if(incoming_action == 'one'):

            data_returned['action'] += "-ONE"

            auth.clear()

            try:
                auth.token = incoming_data['hash']
            except Exception as ex:
                
                data_returned['return'] = False
                data_returned['code'] = 502
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)
            
            
            data = auth.is_authorized()
            
            if(data[0] == False):
            
                data_returned['return'] = False
                data_returned['code'] = 501
                data_returned['message'] = data[1]
            
            else:
                
                user_credential_ref = User_Credential.objects.filter(user_credential_id=int(data[1]))
                user_credential_ref = user_credential_ref[0]
                user_credential_ref.delete()
                
                data_returned['return'] = True
                data_returned['code'] = 200
        
        else:
            data_returned['return'] = False
            data_returned['code'] = 402
        
        return JsonResponse(data_returned, safe=True)

    else:

        data_returned = dict()
        data_returned['return'] = False
        data_returned['code'] = 402
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def admin_API(request, id=0):
    global auth
    data_returned = dict()

    if(request.method == 'FETCH'):

        data_returned['action'] = "FETCH"

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        try:
            incoming_action = user_data["action"]
            incoming_data = user_data["data"]
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        if(incoming_action == 'get_one'):
            data_returned['action'] += '-GET_ONE'
            
            auth.clear()

            try:
                auth.token = incoming_data['hash']
            except Exception as ex:
                
                data_returned['return'] = False
                data_returned['code'] = 502
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            data = auth.is_authorized_admin()

            if(data[0] == True):

                admin_credential_ref = Admin_Credential.objects.filter(admin_credential_id = int(data[1]))
                admin_credential_ref = admin_credential_ref[0]

                data_returned['return'] = True
                data_returned['code'] = 200
                data_returned['data'] = Admin_Credential_Serializer(admin_credential_ref, many=False).data

                del(data_returned['data']['admin_credential_id'])


            else:

                data_returned['return'] = False
                data_returned['code'] = 501
                data_returned['message'] = data[1]
        
        elif(incoming_action == 'get_all'):
            data_returned['action'] += '-GET_ALL'

            auth.clear()

            try:
                auth.token = incoming_data['hash']
            except Exception as ex:
                
                data_returned['return'] = False
                data_returned['code'] = 502
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)

            data = auth.is_alpha_admin()

            if(data[0] == True):

                admin_credential_ref = Admin_Credential.objects.all()
                admin_credential_serialized = Admin_Credential_Serializer(admin_credential_ref, many=True)

                data_returned['return'] = True
                data_returned['code'] = 200
                data_returned['data'] = dict()

                i = 0
                for data in admin_credential_serialized.data:
                    data_returned['data'][i] = dict(data)
                    del(data_returned['data'][i]['admin_credential_id'])
                    i += 1

            else:

                data_returned['return'] = False
                data_returned['code'] = 501
                data_returned['message'] = data[1]    
        
        else:
            data_returned['return'] = False
            data_returned['code'] = 402
            
        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'POST'):

        data_returned['action'] = "POST"

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        try:
            incoming_hash = user_data['hash']
            incoming_data = user_data["data"]
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        auth.clear()
        try:
            auth.token = incoming_hash
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        data = auth.is_authorized_admin()
        if(data[0] == False):

            data_returned['return'] = False
            data_returned['code'] = 501
            data_returned['message'] = data[1]
            
        else:

            data = auth.is_alpha_admin()
            if(data[0] == False):

                data_returned['return'] = False
                data_returned['code'] = 405
                data_returned['message'] = data[1]
            
            else:

                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(incoming_data['user_id']))
                if(len(user_credential_ref) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = 406
                
                else:
                    user_credential_ref = user_credential_ref[0]
                    admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = user_credential_ref)
                    if(len(admin_credential_ref) > 0):
                        
                        data_returned['return'] = False
                        data_returned['code'] = 408

                    else:
                        admin_credential_ref_new = Admin_Credential(user_credential_id = user_credential_ref,
                                                                    privilege_id_1 = None,
                                                                    privilege_id_2 = None,
                                                                    privilege_id_3 = None)
                        admin_credential_ref_new.save()
                    
                        data_returned['return'] = True
                        data_returned['code'] = 200

        return JsonResponse(data_returned, safe=True)
   
    elif(request.method == 'PUT'):

        data_returned['action'] = "PUT"

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        auth.clear()

        try:
            auth.token = user_data['hash']
            incoming_data = user_data["data"]
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.is_authorized_admin()
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 501
            data_returned['message'] = data[1]

            return JsonResponse(data_returned, safe=True)

        else:

            admin_credential_ref = Admin_Credential.objects.get(admin_credential_id = int(data[1]))

            if(admin_credential_ref.user_credential_id.user_credential_id == incoming_data['user_credential_id']):
                admin_credential_de_serialized = Admin_Credential_Serializer(admin_credential_ref, data=incoming_data)
                flag = True
            
            else:
                data = auth.is_alpha_admin()
                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 405
                    data_returned['message'] = data[1]

                    return JsonResponse(data_returned, safe=True)
                
                else:
                    user_credential_ref = User_Credential.objects.filter(user_credential_id = incoming_data['user_credential_id'])
                    if(len(user_credential_ref) < 1):
                        data_returned['return'] = False
                        data_returned['code'] = 406
                    
                    else:
                        user_credential_ref = user_credential_ref[0]
                        admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = user_credential_ref)
                        if(len(admin_credential_ref) < 1):
                            data_returned['return'] = False
                            data_returned['code'] = 407
                        
                        else:
                            admin_credential_ref = admin_credential_ref[0]
                            admin_credential_de_serialized = Admin_Credential_Serializer(admin_credential_ref, data=incoming_data)
                            flag = True

            if(flag == True):
                if(admin_credential_de_serialized.initial_data['privilege_id_1'] == 2):
                    intr = 1
                elif(admin_credential_de_serialized.initial_data['privilege_id_2'] == 2):
                    intr = 2
                elif(admin_credential_de_serialized.initial_data['privilege_id_3'] == 2):
                    intr = 3
                else:
                    intr = 0
            
                if(intr == 0):
                    pass
                else:
                    data = auth.is_alpha_admin()
                    if(data[0] == False):
                        data_returned['return'] = False
                        data_returned['code'] = 405
                        data_returned['message'] = "[x] Only alpha can cast alpha."

                        return JsonResponse(data_returned, safe=True)
                    else:
                        pass
        
        if(admin_credential_de_serialized.is_valid()):
            admin_credential_de_serialized.save()

            data_returned['return'] = True
            data_returned['code'] = 200

        else:

            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = admin_credential_de_serialized.errors
        
        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'DELETE'):
        
        data_returned['action'] = "DELETE"

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        auth.clear()

        try:
            auth.token = user_data['hash']
            incoming_data = user_data["data"]
        except Exception as ex:
            
            data_returned['return'] = False
            data_returned['code'] = 502
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.is_authorized_admin()
        if(data[0] == False):

            data_returned['return'] = False
            data_returned['code'] = 501
            data_returned['message'] = data[1]

        else:

            admin_credential_ref = Admin_Credential.objects.filter(admin_credential_id = int(data[1]))
            admin_credential_ref = admin_credential_ref[0]

            user_credential_ref = User_Credential.objects.filter(user_credential_id = incoming_data['user_id'])
            if(len(user_credential_ref) < 1):

                data_returned['return'] = False
                data_returned['code'] = 406
                
            else:
                user_credential_ref = user_credential_ref[0]
                if(user_credential_ref.user_credential_id == admin_credential_ref.user_credential_id.user_credential_id):
                    admin_credential_ref.delete()
                    
                    data_returned['return'] = True
                    data_returned['code'] = 200
                
                else:
                    data = auth.is_alpha_admin()
                    if(data[0] == False):

                        data_returned['return'] = False
                        data_returned['code'] = 405
                        data_returned['message'] = data[1]
                    
                    else:

                        admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = user_credential_ref)
                        if(len(admin_credential_ref) < 1):

                            data_returned['return'] = False
                            data_returned['code'] = 407

                        else:

                            admin_credential_ref = admin_credential_ref[0]
                            admin_credential_ref.delete()

                            data_returned['return'] = True
                            data_returned['code'] = 200

        return JsonResponse(data_returned, safe=True)
    
    else:

        data_returned = dict()
        data_returned['return'] = False
        data_returned['code'] = 402
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def admin_privilege_API(request, id=0):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        data_returned['action'] = "GET"
        data_returned['return'] = True
        data_returned['data'] = dict()

        admin_privilege_ref = Admin_Privilege.objects.all()
        admin_privilege_serialized = Admin_Privilege_Serializer(admin_privilege_ref, many=True)

        i=0
        for priv in admin_privilege_serialized.data:
            data_returned['data'][i] = priv
            i+=1

        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'POST'):

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        auth.clear()
        try:
            data_returned['action'] = "POST"
            incoming_hash = user_data['hash']
            incoming_data = user_data['data']
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        data = auth.is_alpha_admin()
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 405
            data_returned['message'] = data[1]
        else:
            admin_privilege_de_serialized = Admin_Privilege_Serializer(data=incoming_data, many=False)
            try:
                admin_privilege_de_serialized.initial_data['admin_privilege_name'] = admin_privilege_de_serialized.initial_data['admin_privilege_name'].lower()
            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 404
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)
            else:
                if(admin_privilege_de_serialized.is_valid()):
                    admin_privilege_de_serialized.save()
                    
                    data_returned['return'] = True
                    data_returned['code'] = 200
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 502
                    data_returned['message'] = admin_privilege_de_serialized.errors
        
        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'PUT'):

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        auth.clear()
        try:
            data_returned['action'] = "PUT"
            incoming_hash = user_data['hash']
            incoming_data = user_data['data']
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.is_alpha_admin()
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 405
            data_returned['message'] = data[1]
        else:

            try:
                admin_privilege_ref = Admin_Privilege.objects.get(admin_privilege_id = incoming_data['admin_privilege_id'])
            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 404
                data_returned['message'] = str(ex)

                return JsonResponse(data_returned, safe=True)
            else:

                admin_privilege_de_serialized = Admin_Privilege_Serializer(admin_privilege_ref, data=incoming_data)
                if(admin_privilege_de_serialized.is_valid()):
                    admin_privilege_de_serialized.save()
                    
                    data_returned['return'] = True
                    data_returned['code'] = 200
                else:
                    data_returned['return'] = False
                    data_returned['code'] = 502
                    data_returned['message'] = admin_privilege_de_serialized.errors
                
        return JsonResponse(data_returned, safe=True)
    
    elif(request.method == 'DELETE'):

        try:
            user_data = JSONParser().parse(request)
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)
        
        auth.clear()
        try:
            data_returned['action'] = "DELETE"
            incoming_hash = user_data['hash']
            incoming_data = user_data['data']
            auth.token = incoming_hash
        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)

            return JsonResponse(data_returned, safe=True)

        data = auth.is_alpha_admin()
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 405
            data_returned['message'] = data[1]
        else:
            if(int(incoming_data['admin_privilege_id']) == 2):
                data_returned['return'] = False
                data_returned['code'] = 503
            else:

                try:
                    admin_privilege_ref = Admin_Privilege.objects.get(admin_privilege_id = incoming_data['admin_privilege_id'])
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 404
                    data_returned['message'] = str(ex)

                    return JsonResponse(data_returned, safe=True)
                else:
                    admin_privilege_ref.delete()
                    data_returned['return'] = True
                    data_returned['code'] = 200

        return JsonResponse(data_returned, safe=True)
    
    else:

        data_returned = dict()
        data_returned['return'] = False
        data_returned['code'] = 402
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)