from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
# ------------------------------------------------------
from content_delivery.models import Coordinator, Subject, Subject_Coordinator_Int
from content_delivery.serializer import Coordinator_Serializer, Subject_Serializer

from auth_prime.authorize import Authorize

from auth_prime.models import User_Credential, Admin_Credential, Admin_Cred_Admin_Prev_Int, Admin_Privilege

# ------------------------------------------------------
auth = Authorize()
API_VERSION = "1.0"
# ------------------------------------------------------

# ---------------------------------------------API SPACE-------------------------------------------------------

@csrf_exempt
def coordinator_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'POST'):
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
            user_ids = list(incoming_data["user_credential_id"])
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
        
        data = auth.check_authorization("admin") # Coordinators can be placed by admins only
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(data[1])) # for user is admin
            if(len(admin_credential_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 111
            else:
                admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = 'COPG') # for COPG privilege exists
                if(len(admin_privilege_ref) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = 116
                    data_returned['message'] = 'ASK admin to create COPG privilege.'
                else:
                    admin_credential_ref = admin_credential_ref[0]
                    admin_privilege_ref = admin_privilege_ref[0]
                    many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id,
                                                                                admin_privilege_id = admin_privilege_ref.admin_privilege_id) # for the hash admin has the privilege
                    if(len(many_to_many_ref) < 1):
                        data_returned['return'] = False
                        data_returned['code'] = 118
                    else:

                        data_returned['return'] = list()
                        data_returned['code'] = list()

                        for user_id in user_ids:
                            try:
                                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(user_id))
                            except Exception as ex:
                                data_returned['return'].append(False)
                                data_returned['code'].append(404)
                                data_returned['message'] = str(ex)

                                return JsonResponse(data_returned, safe=True)

                            else:
                                if(len(coordinator_ref) > 0):
                                    data_returned['return'].append(False)
                                    data_returned['code'].append(101)
                                else:
                                    user_credential_ref = User_Credential.objects.filter(user_credential_id=int(user_id))
                                    if(len(user_credential_ref) < 1):
                                        data_returned['return'].append(False)
                                        data_returned['code'].append(114)
                                    else:
                                        user_credential_ref = user_credential_ref[0]
                                        coordinator_ref_new = Coordinator(user_credential_id = user_credential_ref)
                                        coordinator_ref_new.save()

                                        data_returned['return'].append(True)
                                        data_returned['code'].append(100)

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
        
        try:
            user_ids = list(incoming_data["user_credential_id"])
        except Exception:
            data = auth.check_authorization("user")
            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 102
            else:
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = 103
                else:
                    coordinator_ref = coordinator_ref[0]
                    coordinator_ref.delete()

                    data_returned['return'] = True
                    data_returned['code'] = 100
        else:
            data = auth.check_authorization("admin") # Coordinators can be placed by admins only
            if(data[0] == False):
                data_returned['return'] = False
                data_returned['code'] = 102
            else:
                admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(data[1])) # for user is admin
                if(len(admin_credential_ref) < 1):
                    data_returned['return'] = False
                    data_returned['code'] = 111
                else:
                    admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = 'COPG') # for COPG privilege exists
                    if(len(admin_privilege_ref) < 1):
                        data_returned['return'] = False
                        data_returned['code'] = 116
                        data_returned['message'] = 'ASK admin to create COPG privilege.'
                    else:
                        admin_credential_ref = admin_credential_ref[0]
                        admin_privilege_ref = admin_privilege_ref[0]
                        many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id,
                                                                                    admin_privilege_id = admin_privilege_ref.admin_privilege_id) # for the hash admin has the privilege
                        if(len(many_to_many_ref) < 1):
                            data_returned['return'] = False
                            data_returned['code'] = 118
                        else:

                            data_returned['return'] = list()
                            data_returned['code'] = list()

                            for user_id in user_ids:
                                try:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(user_id))
                                except Exception as ex:
                                    data_returned['return'].append(False)
                                    data_returned['code'].append(404)
                                    data_returned['message'] = str(ex)

                                    return JsonResponse(data_returned, safe=True)

                                else:
                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'].append(False)
                                        data_returned['code'].append(103)
                                    else:
                                        coordinator_ref = coordinator_ref[0]
                                        coordinator_ref.delete()

                                        data_returned['return'].append(True)
                                        data_returned['code'].append(100)

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
            user_ids = list(incoming_data["user_credential_id"])
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
        
        data = auth.check_authorization("user") # Coordinators can be checked by everyone
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            if(0 in user_ids):
                coordinator_ref = Coordinator.objects.all()
                coordinator_serialized = Coordinator_Serializer(coordinator_ref, many=True)

                data_returned['return'] = True
                data_returned['code'] = 100
                data_returned['data'] = coordinator_serialized.data
            else:
                data_returned['return'] = list()
                data_returned['code'] = list()
                data_returned['data'] = list()

                for user_id in user_ids:
                    try:
                        coordinator_ref = Coordinator.objects.filter(user_credential_id = int(user_id))
                    except Exception as ex:
                        data_returned['return'].append(False)
                        data_returned['code'].append(404)
                        data_returned['message'] = str(ex)

                        return JsonResponse(data_returned, safe=True)

                    else:
                        if(len(coordinator_ref) < 1):
                            data_returned['return'].append(False)
                            data_returned['code'].append(101)
                            data_returned['data'].append(None)
                        else:
                            coordinator_ref = coordinator_ref[0]
                            coordinator_serialized = Coordinator_Serializer(coordinator_ref, many=False)
                            data_returned['return'].append(True)
                            data_returned['code'].append(100)
                            data_returned['data'].append(coordinator_serialized.data)

        return JsonResponse(data_returned, safe=True)
    
    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def subject_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'POST'):
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
        
        data = auth.check_authorization("admin") # admin + coordinators can add or remove subjects
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))

            if(len(coordinator_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 103
            else:
                try:
                    incoming_data['subject_name'] = incoming_data['subject_name'].upper()
                    incoming_data['subject_description'] = incoming_data['subject_description'].lower()
                    subject_ref = Subject.objects.filter(subject_name__contains = incoming_data['subject_name'])
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 402
                    data_returned['message'] = str(ex)
                    
                    return JsonResponse(data_returned, safe=True)
                
                if(len(subject_ref) < 1):
                    
                    try: # some special job
                        name = incoming_data['subject_name'].split(" ")
                        name = [x[0] for x in name]
                        name = "".join(name)
                        
                        temp = Subject.objects.filter(subject_name__contains = name)
                        if(len(temp) > 0):
                            temp = temp[0]
                            temp = int(temp.subject_name.split(name)[1]) + 1
                        else:
                            temp = 1

                        incoming_data['subject_name'] = f"{incoming_data['subject_name']} {name}{temp}"
                    except Exception as ex:
                        print(">>> ",ex)

                    subject_de_serialized = Subject_Serializer(data=incoming_data)
                    
                    if(subject_de_serialized.is_valid()):
                        subject_de_serialized.save()
                        
                        sub_id = subject_de_serialized.data['subject_id']
                        cod_id = coordinator_ref[0].coordinator_id
                        many_to_many_ref = Subject_Coordinator_Int.objects.filter(subject_id = int(sub_id), coordinator_id = int(cod_id))
                        if(len(many_to_many_ref) > 0):
                            data_returned['return'] = False
                            data_returned['code'] = 119
                        else:
                            subject_ref = Subject.objects.get(subject_id = int(sub_id))
                            many_to_many_ref_new = Subject_Coordinator_Int(subject_id = subject_ref, coordinator_id = coordinator_ref[0])
                            many_to_many_ref_new.save()
                            
                            data_returned['return'] = True
                            data_returned['code'] = 100
                    else:
                        data_returned['return'] = False
                        data_returned['code'] = 405
                        data_returned['message'] = subject_de_serialized.errors
                else:                    
                    data_returned['return'] = False
                    data_returned['code'] = 108
        
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
            subject_ids = incoming_data["subject_id"]
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

        try:
            auth.token = incoming_hash
        except Exception as ex:                    
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)
            
            return JsonResponse(data_returned, safe=True)
        
        data = auth.check_authorization("admin") # admin + coordinators can add or remove subjects
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))

            if(len(coordinator_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 103
            else:
                data_returned['return'] = list()
                data_returned['code'] = list()
                
                for sub in subject_ids:
                    try:
                        subject_ref = Subject.objects.filter(subject_id=int(sub))
                        if(len(subject_ref) < 1):
                            data_returned['return'].append(False)
                            data_returned['code'].append(107)
                        else:
                            subject_ref = subject_ref[0]
                            subject_ref.delete()

                            data_returned['return'].append(True)
                            data_returned['code'].append(100)
                    except Exception as ex:
                        data_returned['return'].append(False)
                        data_returned['code'].append(404)
                        data_returned['message'] = str(ex)

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
        
        try:
            incoming_data = user_data["data"]
            incoming_hash = incoming_data["hash"]
            subject_ids = incoming_data["subject_id"]
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

        try:
            auth.token = incoming_hash
        except Exception as ex:                    
            data_returned['return'] = False
            data_returned['code'] = 404
            data_returned['message'] = str(ex)
            
            return JsonResponse(data_returned, safe=True)
        
        data = auth.check_authorization("user") # every one can see subject data
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            if(0 in subject_ids):
                subject_ref = Subject.objects.all()
                subject_serialized = Subject_Serializer(subject_ref, many=True)

                data_returned['return'] = True
                data_returned['code'] = 100
                data_returned['data'] = subject_serialized.data
            else:
                data_returned['return'] = list()
                data_returned['code'] = list()
                data_returned['data'] = list()

                for sub in subject_ids:
                    try:
                        subject_ref = Subject.objects.filter(subject_id = int(sub))
                        if(len(subject_ref) < 1):
                            data_returned['return'].append(False)
                            data_returned['code'].append(107)
                            data_returned['data'].append(None)
                        else:
                            subject_ref = subject_ref[0]
                            subject_serialized = Subject_Serializer(subject_ref, many=False)
                            
                            data_returned['return'].append(True)
                            data_returned['code'].append(100)
                            data_returned['data'].append(subject_serialized.data)
                        
                    except Exception as ex:
                        data_returned['return'].append(False)
                        data_returned['code'].append(404)
                        data_returned['data'].append(None)
                        data_returned['message'] = str(ex)

                        return JsonResponse(data_returned, safe=True)
        
        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)


@csrf_exempt
def subject_n_coordinator(request):
    pass
# ---------------------------------------------VIEW SPACE-------------------------------------------------------
