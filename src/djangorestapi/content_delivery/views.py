from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
# ------------------------------------------------------
from content_delivery.models import Coordinator, Subject

from auth_prime.authorize import Authorize

from auth_prime.models import User_Credential, Admin_Credential
# ------------------------------------------------------
auth = Authorize()
API_VERSION = "1.0"
# ------------------------------------------------------
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
            incoming_hash = user_data["hash"]
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
        
        data = auth.is_authorized_admin(key="COA") # Coordinators can be placed by admins only
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))            
            coordinator_ref = Coordinator.objects.filter(user_credential_id = user_credential_ref)
            if(len(coordinator_ref) > 0):
                data_returned['return'] = False
                data_returned['code'] = 101
            else:
                coordinator_ref_new = Coordinator(user_credential_id = user_credential_ref)
                coordinator_ref_new.save()

                data_returned['return'] = True
                data_returned['code'] = 100
                data_returned['data'] = {'coordinator_id' : coordinator_ref.coordinator_id}

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
            incoming_hash = user_data["hash"]
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
        
        data = auth.is_authorized() # self delete of coordinator id
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))            
            coordinator_ref = Coordinator.objects.filter(user_credential_id = user_credential_ref)
            if(len(coordinator_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 103
            else:
                coordinator_ref = coordinator_ref[0]
                coordinator_ref.delete()

                data_returned['return'] = True
                data_returned['code'] = 100
            
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
            incoming_hash = user_data["hash"]
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
        
        data = auth.is_authorized() # self fetch coordinator id
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))            
            coordinator_ref = Coordinator.objects.filter(user_credential_id = user_credential_ref)
            if(len(coordinator_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 103
            else:
                coordinator_ref = coordinator_ref[0]
                data_returned['return'] = True
                data_returned['code'] = 100
                data_returned['data'] = {"coordinator_id" : coordinator_ref.coordinator_id}

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
            incoming_hash = user_data["hash"]
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
        
        data = auth.is_authorized()
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
            coordinator_ref = Coordinator.objects.filter(user_credential_id = user_credential_ref) # coordinator permitted to add subjects

            if(len(coordinator_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 103
            else:
                try:
                    subject_ref = Subject.objects.filter(subject_name__icontains = incoming_data['subject_name'].lower())
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 402
                    data_returned['message'] = str(ex)
                    
                    return JsonResponse(data_returned, safe=True)
                
                if(len(subject_ref) < 1):
                    subject_ref_new = Subject(coordinator_id_1 = coordinator_ref[0],
                                              subject_name = incoming_data['subject_name'].lower(),
                                              subject_description = incoming_data['subject_desctiption'])
                    subject_ref_new.save()

                    data_returned['return'] = True
                    data_returned['code'] = 100
                else:
                    subject_ref = subject_ref[0]
                    
                    data_returned['return'] = False
                    data_returned['code'] = 108
                    data_returned['data'] = {"subject_id" : subject_ref.subject_id}
        
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
            incoming_hash = user_data["hash"]
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
        
        data = auth.is_authorized_admin() # only admins authorised to delete subjects
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            try:
                subject_ref = Subject.objects.filter(subject_id = int(incoming_data['subject_id']))
            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = str(ex)
                    
                return JsonResponse(data_returned, safe=True)
                
            if(len(subject_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 107
            else:
                subject_ref = subject_ref[0]
                subject_ref.delete()
                    
                data_returned['return'] = True
                data_returned['code'] = 100
                
        
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
            incoming_hash = user_data["hash"]
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
        
        data = auth.is_authorized() # self fetch coordinator id
        if(data[0] == False):
            data_returned['return'] = False
            data_returned['code'] = 102
        else:
            user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))            
            coordinator_ref = Coordinator.objects.filter(user_credential_id = user_credential_ref)
            if(len(coordinator_ref) < 1):
                data_returned['return'] = True
                data_returned['code'] = 103
                data_returned['data'] = None
            else:
                data_returned['return'] = True
                data_returned['code'] = 100
                data_returned['data'] = None
                

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "[x] parent action invalid."

        return JsonResponse(data_returned, safe=True)


            
