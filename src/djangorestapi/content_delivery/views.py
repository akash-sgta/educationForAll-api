from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

# ------------------------------------------------------
from content_delivery.models import Coordinator
from content_delivery.models import Subject
from content_delivery.models import Subject_Coordinator_Int
from content_delivery.models import Forum
from content_delivery.models import Reply
from content_delivery.models import Lecture
from content_delivery.models import Assignment
from content_delivery.models import Post

from content_delivery.serializer import Coordinator_Serializer
from content_delivery.serializer import Subject_Serializer
from content_delivery.serializer import Forum_Serializer
from content_delivery.serializer import Reply_Serializer
from content_delivery.serializer import Lecture_Serializer
from content_delivery.serializer import Assignment_Serializer
from content_delivery.serializer import Post_Serializer

from auth_prime.authorize import Authorize

from auth_prime.models import User_Credential
from auth_prime.models import Admin_Credential
from auth_prime.models import Admin_Cred_Admin_Prev_Int
from auth_prime.models import Admin_Privilege

# ------------------------------------------------------
auth = Authorize()
# ------------------------------------------------------

# ---------------------------------------------API SPACE-------------------------------------------------------

@csrf_exempt
def coordinator_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = 'ERROR-Invalid-GET Not supported'
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = f"ERROR-Parsing-{str(ex)}"
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = f"ERROR-Api-{data[1]}"
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
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("admin") # Coordinators can be placed by admins only
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 111
                                    data_returned['message'] = f"ERROR-Hash-not ADMIN"
                                    return JsonResponse(data_returned, safe=True)

                                else:
                                    admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1])) # for user is admin
                                    admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = 'CAGP') # for COPG privilege exists
                                    
                                    if(len(admin_privilege_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 116
                                        data_returned['message'] = 'ERROR-NotFound-CAGP privilege'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        admin_privilege_ref = admin_privilege_ref[0]
                                        many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id,
                                                                                                    admin_privilege_id = admin_privilege_ref.admin_privilege_id) # for the hash admin has the privilege
                                        
                                        if(len(many_to_many_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 118
                                            data_returned['message'] = 'ERROR-Pair-Not Found Admin Credential <=> Admin PRIVILEGE'
                                            return JsonResponse(data_returned, safe=True)
                            
                                        else:
                                            try:
                                                user_ids = tuple(set(incoming_data['user_id']))
                                            
                                            except Exception as ex:
                                                data_returned['return'] = False
                                                data_returned['code'] = 404
                                                data_returned['message'] = f"ERROR-Amiguous-{str(ex)}"
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                if(len(user_ids) < 1):
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 151
                                                    data_returned['message'] = "ERROR-Empty-At least one id required"
                                                    return JsonResponse(data_returned, safe=True)
                                                
                                                else:
                                                    data_returned['data'] = dict()
                                                    temp = dict()

                                                    for id in user_ids:
                                                        try:
                                                            coordinator_ref = Coordinator.objects.filter(user_credential_id = int(id))
                                                        
                                                        except Exception as ex:
                                                            temp['return'] = False
                                                            temp['code'] = 408
                                                            temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()
                                                        
                                                        else:
                                                            if(len(coordinator_ref) > 0):
                                                                temp['return'] = False
                                                                temp['code'] = 101
                                                                temp['message'] = "ERROR-Ambiguous-USER already CORDINATOR"
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                                            
                                                            else:
                                                                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                                    
                                                                if(len(user_credential_ref) < 1):
                                                                    temp['return'] = False
                                                                    temp['code'] = 114
                                                                    temp['message'] = "ERROR-Invalid-USER id"
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()
                                            
                                                                else:
                                                                    user_credential_ref = user_credential_ref[0]
                                                                    coordinator_ref_new = Coordinator(user_credential_id = user_credential_ref)
                                                                    coordinator_ref_new.save()

                                                                    temp['return'] = True
                                                                    temp['code'] = 100
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()

                                return JsonResponse(data_returned, safe=True)
    
                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                if('user_id' in incoming_data.keys()): # force delete
                                    try:
                                        user_ids = tuple(set(incoming_data["user_id"]))
                                    
                                    except Exception as ex:
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = f"ERROR-Ambiguous-{str(ex)}"
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        if(len(user_ids) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 151
                                            data_returned['message'] = "ERROR-Empty-Atleast one id reqired"
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            data = auth.check_authorization("admin") # Coordinators can be removed by admins
                                            
                                            if(data[0] == False):
                                                data_returned['return'] = False
                                                data_returned['code'] = 102
                                                data_returned['message'] = "ERROR-Hash-not ADMIN"
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1])) # for user is admin
                                                admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = 'CAGP') # for CAPG privilege exists
                                                
                                                if(len(admin_privilege_ref) < 1):
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 116
                                                    data_returned['message'] = 'ERROR-NotFound-CAGP privilege'
                                                    return JsonResponse(data_returned, safe=True)
                                
                                                else:
                                                    admin_privilege_ref = admin_privilege_ref[0]
                                                    many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id,
                                                                                                                admin_privilege_id = admin_privilege_ref.admin_privilege_id) # for the hash admin has the privilege
                                                    
                                                    if(len(many_to_many_ref) < 1):
                                                        data_returned['return'] = False
                                                        data_returned['code'] = 118
                                                        data_returned['message'] = 'ERROR-Pair-Not Found Admin Credential <=> Admin Privilege pair'
                                                        return JsonResponse(data_returned, safe=True)
                                                    
                                                    else:
                                                        data_returned['data'] = dict()
                                                        temp = dict()

                                                        for id in user_ids:
                                                            try:
                                                                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(id))
                                            
                                                            except Exception as ex:
                                                                temp['return'] = False
                                                                temp['code'] = 408
                                                                temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                                            
                                                            else:
                                                                if(len(coordinator_ref) < 1):
                                                                    temp['return'] = False
                                                                    temp['code'] = 103
                                                                    temp['message'] = "ERROR-Invalid-Coordinate id"
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()
                                                                
                                                                else:
                                                                    coordinator_ref = coordinator_ref[0]
                                                                    coordinator_ref.delete()

                                                                    temp['return'] = True
                                                                    temp['code'] = 100
                                                                    data_returned['data'][id] = temp.copy()
                                                                    temp.clear()
                                
                                else: # self delete
                                    data = auth.check_authorization("user")
                                    
                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 102
                                        data_returned['message'] = 'ERROR-Hash-not USER'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                                        
                                        if(len(coordinator_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 103
                                            data_returned['message'] = 'ERROR-NotFound-USER not COORDINATOR'
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            coordinator_ref = coordinator_ref[0]
                                            coordinator_ref.delete()

                                            data_returned['return'] = True
                                            data_returned['code'] = 100            

                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                if('user_id' in incoming_data.keys()): # force fetch
                                    try:
                                        user_ids = tuple(set(incoming_data["user_id"]))
                                    
                                    except Exception as ex:
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = f"ERROR-Ambiguous-{str(ex)}"
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:

                                        if(len(user_ids) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 151
                                            data_returned['message'] = "ERROR-Empty-Atleast one id required"
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            data = auth.check_authorization("user")
                                            # from parent
                                            if(data[0] == False):
                                                data_returned['return'] = False
                                                data_returned['code'] = 102
                                                data_returned['message'] = "ERROR-Hash-not USER"
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                data_returned['data'] = dict()
                                                temp = dict()
                                                
                                                if(0 in user_ids):
                                                    coordinator_ref_all = Coordinator.objects.all()
                                                    
                                                    if(len(coordinator_ref_all) < 1):
                                                        temp['return'] = False
                                                        temp['code'] = 151
                                                        temp['message'] = 'ERROR-Empty-Coordinator Tray'
                                                        data_returned['data'][0] = temp.copy()
                                                        temp.clear()
                                                        return JsonResponse(data_returned, safe=True)

                                                    else:
                                                        coordinator_serialized = Coordinator_Serializer(coordinator_ref_all, many=True).data
                                                        temp_2 = list()
                                                        temp['return']= True
                                                        temp['code'] = 100
                                                        temp['data'] = coordinator_serialized
                                                        data_returned['data'][0] = temp.copy()
                                                        temp.clear()
                                                
                                                else:
                                                    for id in user_ids:
                                                        try:
                                                            coordinator_ref = Coordinator.objects.filter(user_credential_id = int(id))
                                            
                                                        except Exception as ex:
                                                            temp['return'] = False
                                                            temp['code'] = 408
                                                            temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()
                                                            
                                                        else:
                                                            if(len(coordinator_ref) < 1):
                                                                temp['return'] = False
                                                                temp['code'] = 103
                                                                temp['message'] = "ERROR-Invalid-Coordinate id"
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                                                
                                                            else:
                                                                coordinator_ref = coordinator_ref[0]
                                                                coordinator_serialized = Coordinator_Serializer(coordinator_ref, many=False).data

                                                                temp['return'] = True
                                                                temp['code'] = 100
                                                                temp['data'] = coordinator_serialized
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()
                                
                                else: # self fetch
                                    data = auth.check_authorization("user")
                                    
                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 102
                                        data_returned['message'] = 'ERROR-Hash-not USER'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                                        
                                        if(len(coordinator_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 103
                                            data_returned['message'] = 'ERROR-NotFound-USER not COORDINATOR'
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            coordinator_ref = coordinator_ref[0]
                                            coordinator_serialized = Coordinator_Serializer(coordinator_ref, many=False).data

                                            data_returned['return'] = True
                                            data_returned['code'] = 100
                                            data_returned['data'] = coordinator_serialized

                                return JsonResponse(data_returned, safe=True)
                        
                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("admin")
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = "ERROR-Hash-not ADMIN"
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__icontains = 'CAGP')
                                    if(len(admin_privilege_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 116
                                        data_returned['message'] = 'ERROR-NotFound-Admin Privilege CAGP'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1]))
                                        admin_privilege_ref = admin_privilege_ref[0]
                                        self_many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref, admin_privilege_id = admin_privilege_ref.admin_privilege_id)

                                        if(len(self_many_to_many_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 118
                                            data_returned['message'] = 'ERROR-Pair-Not exist Admin Credential <=> Admin Privilege'
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            if('updates' not in incoming_data.keys()):
                                                data_returned['return'] = False
                                                data_returned['code'] = 402
                                                data_returned['message'] = 'ERROR-Key-Updates required'
                                                return JsonResponse(data_returned, safe=True)
                                
                                            else:
                                                data_returned['data'] = dict()
                                                temp = dict()

                                                updates = tuple(incoming_data['updates'])
                                                if(len(updates) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 151
                                                    temp['message'] = "ERROR-Empty-At least one update required"
                                                    data_returned['data'] = temp.copy()
                                                    temp.clear()
                                                    return JsonResponse(data_returned, safe=True)
                                    
                                                else:
                                                    for update in updates:
                                                        try:
                                                            coordinator_ref = Coordinator.objects.filter(coordinator_id = int(update['coordinator_id']))
                                                            subject_ref = Subject.objects.filter(subject_id = int(update['subject_id']))
                                                        
                                                        except Exception as ex:
                                                            temp['return'] = False
                                                            temp['code'] = 408
                                                            temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                            data_returned['data'] = temp.copy()
                                                            temp.clear()
                                                        
                                                        else:
                                                            if(len(coordinator_ref) < 1):
                                                                temp['return'] = False
                                                                temp['code'] = 114
                                                                temp['message'] = 'ERROR-Invalid-Coordinator id'
                                                                data_returned['data'] = temp.copy()
                                                                temp.clear()

                                                            else:
                                                                if(len(subject_ref) < 1):
                                                                    temp['return'] = False
                                                                    temp['code'] = 114
                                                                    temp['message'] = 'ERROR-Invalid-Subject id'
                                                                    data_returned['data'] = temp.copy()
                                                                    temp.clear()
                                                                
                                                                else:
                                                                    coordinator_ref = coordinator_ref[0]
                                                                    subject_ref = subject_ref[0]

                                                                    many_to_many_ref = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_ref.coordinator_id,
                                                                                                                                  subject_id = subject_ref.subject_id)
                                                                    if(len(many_to_many_ref) > 0):
                                                                        temp['return'] = False
                                                                        temp['code'] = 404
                                                                        temp['message'] = 'ERROR-Pair-Exists Coordinator <=> Subject'
                                                                        data_returned['data'] = temp.copy()
                                                                        temp.clear()
                                                                    
                                                                    else:
                                                                        many_to_many_ref_new = Subject_Coordinator_Int(coordinator_id = coordinator_ref,
                                                                                                                       subject_id = subject_ref)
                                                                        many_to_many_ref_new.save()

                                                                        temp['return'] = True
                                                                        temp['code'] = 100
                                                                        data_returned['data'] = temp.copy()
                                                                        temp.clear()

                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "ERROR-Action-Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = f"ERROR-Ambiguous-{str(ex)}"
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "ERROR-Action-Parent action invalid"
        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def subject_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'): # for only non prime subjects
        data_returned['action'] = request.method.upper()

        subject_ref = Subject.objects.all().exclude(prime=True)
        if(len(subject_ref) < 1):
            data_returned['return'] = False
            data_returned['code'] = 151
            data_returned['message'] = "ERROR-Empty-SUBJECT Tray"
            return JsonResponse(data_returned, safe=True)
        
        else:
            subject_serialized = Subject_Serializer(subject_ref, many=True).data

            data_returned['return'] = True
            data_returned['code'] = 100
            data_returned['data'] = subject_serialized
            return JsonResponse(data_returned, safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = f"ERROR-Parsing-{str(ex)}"
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = f"ERROR-Api-{data[1]}"
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:

                        if(incoming_data["action"].upper() == "CREATE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("admin") # admin + coordinators can add or remove subjects
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not ADMIN'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))

                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 103
                                        data_returned['message'] = 'ERROR-NotFound-USER not COORDINATOR'
                                        return JsonResponse(data_returned, safe=True)
                    
                                    else:
                                        try:
                                            incoming_data['subject_name'] = incoming_data['subject_name'].upper()
                                            incoming_data['subject_description'] = incoming_data['subject_description'].lower()
                                            subject_ref = Subject.objects.filter(subject_name__contains = incoming_data['subject_name'])
                                        
                                        except Exception as ex:
                                            data_returned['return'] = False
                                            data_returned['code'] = 402
                                            data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            if(len(subject_ref) < 1): # new subject
                                                try: # some special job
                                                    name = incoming_data['subject_name'].split()
                                                    name = [word[0] for word in name]
                                                    name = "".join(name)
                                
                                                    temp = Subject.objects.filter(subject_name__contains = name)
                                                    if(len(temp) > 0):
                                                        temp = temp[0]
                                                        temp = int(temp.subject_name.split(name)[1]) + 1
                                                    else:
                                                        temp = 1
                                                
                                                except Exception as ex:
                                                    print(f"[x] SUBJECT CREATION - NAMING - {str(ex)}")
                                                
                                                else:
                                                    incoming_data['subject_name'] = f"{incoming_data['subject_name']} {name}{temp}"
                                                
                                                subject_de_serialized = Subject_Serializer(data=incoming_data)
                            
                                                if(subject_de_serialized.is_valid()):
                                                    subject_de_serialized.save()
                                
                                                    subject_ref = Subject.objects.get(subject_id = int(subject_de_serialized.data['subject_id']))
                                                    coordinator_ref = coordinator_ref[0]
                                                    many_to_many_ref = Subject_Coordinator_Int.objects.filter(subject_id = subject_ref.subject_id, coordinator_id = coordinator_ref.coordinator_id)
                                                    
                                                    if(len(many_to_many_ref) > 0):
                                                        data_returned['return'] = False
                                                        data_returned['code'] = 119
                                                        data_returned['message'] = "ERROR-Pair-Exists Coordinator <=> Subject"
                                                        return JsonResponse(data_returned, safe=True)
                                
                                                    else:
                                                        many_to_many_ref_new = Subject_Coordinator_Int(subject_id = subject_ref, coordinator_id = coordinator_ref)
                                                        many_to_many_ref_new.save()
                                    
                                                        data_returned['return'] = True
                                                        data_returned['code'] = 100
                                                
                                                else:
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 405
                                                    data_returned['message'] = f"ERROR-Parsing-{subject_de_serialized.errors}"
                                                    return JsonResponse(data_returned, safe=True)
                                            
                                            else: # old subject but maybe new admin coordinator
                                                coordinator_ref = coordinator_ref[0]
                                                subject_ref = subject_ref[0]
                                                many_to_many_ref = Subject_Coordinator_Int.objects.filter(subject_id = subject_ref.subject_id, coordinator_id = coordinator_ref.coordinator_id)

                                                if(len(many_to_many_ref) > 0):
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 119
                                                    data_returned['message'] = "Error-Pair-Exists Coordinator <=> Subject"
                                                    return JsonResponse(data_returned, safe=True)
                                
                                                else:
                                                    many_to_many_ref_new = Subject_Coordinator_Int(subject_id = subject_ref, coordinator_id = coordinator_ref)
                                                    many_to_many_ref_new.save()
                                    
                                                    data_returned['return'] = True
                                                    data_returned['code'] = 100
                                                    data_returned['data'] = {"subject" : subject_de_serialized.data['subject_id']}

                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                subject_ids = tuple(set(incoming_data['subject_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                if(len(subject_ids) < 1):
                                    data_returned['return'] = False
                                    data_returned['code'] = 151
                                    data_returned['message'] = 'ERROR-Empty-Atleast one id is required'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    data = auth.check_authorization("admin") # admin + alpha + coordinators can remove subjects

                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 111
                                        data_returned['message'] = f"ERROR-Hash-{data[1]}"
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1]))
                                        admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__icontains = 'ALPHA')

                                        if(len(admin_privilege_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 152
                                            data_returned['message'] = "ERROR-AdminPriv-ALPHA not found"
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            admin_privilege_ref = admin_privilege_ref[0]
                                            many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(admin_privilege_id = admin_privilege_ref.admin_privilege_id,
                                                                                                    admin_credential_id = admin_credential_ref.admin_credential_id)
                                            
                                            if(len(many_to_many) < 1):
                                                data_returned['return'] = False
                                                data_returned['code'] = 118
                                                data_returned['message'] = "ERROR-Pair-Admin Credential<->Admin Privilege not found"
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))

                                                if(len(coordinator_ref) < 1):
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 103
                                                    data_returned['code'] = 'ERROR-NotFound-ADMIN not COORDINATOR'
                                                    return JsonResponse(data_returned, safe=True)

                                                else:
                                                    data_returned['data'] = dict()
                                                    temp = dict()
                                                    
                                                    for id in subject_ids:
                                                        try:
                                                            subject_ref = Subject.objects.filter(subject_id = int(id))

                                                        except Exception as ex:
                                                            temp['return'] = False
                                                            temp['code'] = 408
                                                            temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()
                                                        
                                                        else:
                                                            if(len(subject_ref) < 1):
                                                                temp['return'] = False
                                                                temp['code'] = 107
                                                                temp['message'] = 'ERROR-Invalid-Subject id'
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()

                                                            else:
                                                                subject_ref = subject_ref[0]
                                                                subject_ref.delete()

                                                                temp['return'] = True
                                                                temp['code'] = 100
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()

                                    return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                subject_ids = tuple(set(incoming_data['subject_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                if(len(subject_ids) < 1):
                                    data_returned['return'] = False
                                    data_returned['code'] = 151
                                    data_returned['message'] = 'ERROR-Empty-Atleast one id required'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    data = auth.check_authorization("user") # every one can see subject data

                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 102
                                        data_returned['message'] = 'ERROR-Hash-not USER'
                                        return JsonResponse(data_returned, safe=True)

                                    else:
                                        data_returned['data'] = dict()
                                        temp = dict()

                                        if(0 in subject_ids):
                                            subject_ref = Subject.objects.all()

                                            if(len(subject_ref) < 1):
                                                temp['return'] = False
                                                temp['code'] = 151
                                                temp['message'] = 'ERROR-Empty-SUBJECT Tray'
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                subject_serialized = Subject_Serializer(subject_ref, many=True)

                                                temp['return'] = True
                                                temp['code'] = 100
                                                temp['data'] = subject_serialized.data
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()

                                        else:
                                            for id in subject_ids:
                                                try:
                                                    subject_ref = Subject.objects.filter(subject_id = int(id))
                                                
                                                except Exception as ex:
                                                    temp['return'] = False
                                                    temp['code'] = 408
                                                    temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()
                                                
                                                else:
                                                    if(len(subject_ref) < 1):
                                                        temp['return'] = False
                                                        temp['code'] = 107
                                                        temp['message'] = 'ERROR-Invalid-Subject id'
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()

                                                    else:
                                                        subject_ref = subject_ref[0]
                                                        subject_serialized = Subject_Serializer(subject_ref, many=False).data
                                                        
                                                        temp['return'] = True
                                                        temp['code'] = 100
                                                        temp['data'] = subject_serialized
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()

                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("admin") # admin + coordinators can add or remove subjects
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not ADMIN'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))

                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 103
                                        data_returned['message'] = 'ERROR-NotFound-USER not COORDINATOR'
                                        return JsonResponse(data_returned, safe=True)
                    
                                    else:
                                        try:
                                            subject_ref_self = Subject.objects.filter(subject_id = incoming_data['subject_id'])
                                        
                                        except Exception as ex:
                                            data_returned['return'] = False
                                            data_returned['code'] = 402
                                            data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            if(len(subject_ref_self) < 1):
                                                data_returned['return'] = False
                                                data_returned['code'] = 404
                                                data_returned['message'] = f"ERROR-Invalid-Subject id"
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                subject_ref_self = subject_ref_self[0]
                                                
                                                try:
                                                    incoming_data['subject_name'] = incoming_data['subject_name'].upper()
                                                    incoming_data['subject_description'] = incoming_data['subject_description'].lower()
                                                    subject_ref = Subject.objects.filter(subject_name__icontains = incoming_data['subject_name'])
                                        
                                                except Exception as ex:
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 402
                                                    data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                                    return JsonResponse(data_returned, safe=True)
                                        
                                                else:
                                                    if(len(subject_ref) < 1):
                                                        pass
                                                    
                                                    else: # old subject renaming
                                                        subject_ref = subject_ref[0]

                                                        if(subject_ref.subject_id != subject_ref_self.subject_id):
                                                            data_returned['return'] = False
                                                            data_returned['code'] = 402
                                                            data_returned['message'] = f"ERROR-Found-Subject Name Exists"
                                                            return JsonResponse(data_returned, safe=True)
                                                        
                                                        else:
                                                            pass
                                                    
                                                    try: # some special job
                                                        name = incoming_data['subject_name'].split()
                                                        name = [word[0] for word in name]
                                                        name = "".join(name)
                                            
                                                        temp = Subject.objects.filter(subject_name__contains = name)
                                                        if(len(temp) > 0):
                                                            temp = temp[0]
                                                            temp = int(temp.subject_name.split(name)[1]) + 1
                                                        else:
                                                            temp = 1
                                                            
                                                    except Exception as ex:
                                                        print(f"[x] SUBJECT CREATION - NAMING - {str(ex)}")
                                                            
                                                    else:
                                                        incoming_data['subject_name'] = f"{incoming_data['subject_name']} {name}{temp}"
                                                            
                                                    subject_de_serialized = Subject_Serializer(subject_ref_self, data=incoming_data)
                                        
                                                    if(subject_de_serialized.is_valid()):
                                                        subject_de_serialized.save()
                                                                
                                                        data_returned['return'] = True
                                                        data_returned['code'] = 100
                                                        data_returned['data'] = {"subject" : subject_de_serialized.data['subject_id']}
                                                            
                                                    else:
                                                        data_returned['return'] = False
                                                        data_returned['code'] = 402
                                                        data_returned['message'] = f"ERROR-Serialize-{subject_de_serialized.errors}"
                                                        return JsonResponse(data_returned, safe=True)

                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "ERROR-Action-Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = f"ERROR-Ambiguous-{str(ex)}"
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "ERROR-Action-Parent action invalid"
        return JsonResponse(data_returned, safe=True)

# ------------------------------------------------------------------------------------------------------------

@csrf_exempt
def forum_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = 'ERROR-Invalid-GET Not supported'
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = f"ERROR-Parsing-{str(ex)}"
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = f"ERROR-Api-{data[1]}"
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:

                        if(incoming_data["action"].upper() == "CREATE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user") # only coordinator can add posts

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = 'ERROR-NotFound-USER not COORDINATOR'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        # coordinator_ref = coordinator_ref[0]
                                        forum_de_serialized = Forum_Serializer(data = incoming_data)
                                        if(forum_de_serialized.is_valid()):
                                            forum_de_serialized.save()

                                            data_returned['return'] = True
                                            data_returned['code'] = 100
                                            data_returned['data'] = {"forum" : forum_de_serialized.data['forum_id']}
                                        
                                        else:
                                            data_returned['return'] = False
                                            data_returned['code'] = 405
                                            data_returned['message'] = f"ERROR-Serialize-{forum_de_serialized.errors}"
                                            return JsonResponse(data_returned, safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                forum_ids = tuple(set(incoming_data['forum_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(len(forum_ids) < 1):
                                    data_returned['return'] = False
                                    data_returned['code'] = 151
                                    data_returned['message'] = 'ERROR-Empty-Atleast one id required'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    if(data[0] == False):
                                        data_returned['return'] = False
                                        data_returned['code'] = 102
                                        data_returned['message'] = 'ERROR-Hash-not USER'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        data_returned['data'] = dict()
                                        temp = dict()

                                        for id in forum_ids:
                                            try:
                                                forum_ref = Forum.objects.filter(forum_id = int(id))
                                            
                                            except Exception as ex:
                                                temp['return'] = False
                                                temp['code'] = 408
                                                temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                            
                                            else:
                                                if(len(forum_ref) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 114
                                                    temp['message'] = "ERROR-Invalid-Forum ID"
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()
                                                
                                                else:
                                                    forum_ref = forum_ref[0]
                                                    forum_serialized = Forum_Serializer(forum_ref, many=False).data

                                                    replies_for_forum = Reply.objects.filter(forum_id = forum_ref.forum_id)
                                                    reply_list = list()

                                                    if(len(replies_for_forum) > 0):
                                                        for reply in replies_for_forum:
                                                            reply_list.append(reply.reply_id)

                                                    temp['return'] = True
                                                    temp['code'] = 100
                                                    temp['data'] = {"forum" : forum_serialized, "reply" : reply_list}
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()

                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = 'ERROR-NotFound-USER not COORDINATOR'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        try:
                                            forum_ref = Forum.objects.filter(forum_id = incoming_data['forum_id'])
                                        
                                        except Exception as ex:
                                            data_returned['return'] = False
                                            data_returned['code'] = 402
                                            data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            if(len(forum_ref) < 1):
                                                data_returned['return'] = False
                                                data_returned['code'] = 114
                                                data_returned['message'] = "ERROR-Invalid-Forum ID"
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                forum_ref = forum_ref[0]
                                                forum_de_serialized = Forum_Serializer(forum_ref, data = incoming_data)
                                                if(forum_de_serialized.is_valid()):
                                                    forum_de_serialized.save()

                                                    data_returned['return'] = True
                                                    data_returned['code'] = 100
                                                    data_returned['data'] = {"forum" : forum_de_serialized.data['forum_id']}
                                        
                                                else:
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 405
                                                    data_returned['message'] = f"ERROR-Serialize-{forum_de_serialized.errors}"
                                                    return JsonResponse(data_returned, safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                forum_ids = tuple(set(incoming_data['forum_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))

                                    if(len(forum_ids) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 151
                                        data_returned['message'] = 'ERROR-Empty-Atleast one id required'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        if(len(coordinator_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = 'ERROR-NotFound-USER not COORDINATOR'
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            data_returned['data'] = dict()
                                            temp = dict()

                                            if(0 in forum_ids): # wholesale delete
                                                forum_ref_all = Forum.objects.all()

                                                if(len(forum_ref_all) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 151
                                                    temp['message'] = 'ERROR-Operation-Forum tray empty'
                                                    data_returned['data'][0] = temp.copy()
                                                    temp.clear()
                                                    return JsonResponse(data_returned, safe=True)
                                                
                                                else:
                                                    forum_ref_all.delete()

                                                    temp['return'] = True
                                                    temp['code'] = 100
                                                    temp['data'][id] = temp.copy()
                                                    temp.clear()
                                            
                                            else:
                                                for id in forum_ids:
                                                    try:
                                                        forum_ref = Forum.object.filter(forum_id = int(id))
                                                    
                                                    except Exception as ex:
                                                        temp['return'] = False
                                                        temp['code'] = 151
                                                        temp['message'] = 'ERROR-Empty-Atleast one id required'
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                                    
                                                    else:
                                                        if(len(forum_ref) < 1):
                                                            temp['return'] = False
                                                            temp['code'] = 114
                                                            temp['message'] = 'ERROR-Invalid-FORUM id'
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()
                                                        
                                                        else:
                                                            forum_ref = forum_ref[0]
                                                            forum_ref.delete()

                                                            temp['return'] = True
                                                            temp['code'] = 100
                                                            data_returned['data'][id] = temp.copy()
                                                            temp.clear()

                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "ERROR-Action-Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = f"ERROR-Ambiguous-{str(ex)}"
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "ERROR-Action-Parent action invalid"
        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def reply_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = 'ERROR-Invalid-GET Not supported'
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = f"ERROR-Parsing-{str(ex)}"
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = f"ERROR-Api-{data[1]}"
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:

                        if(incoming_data["action"].upper() == "CREATE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    reply_de_serialized = Reply_Serializer(data = incoming_data)
                                    user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

                                    reply_de_serialized.initial_data['user_credential_id'] = user_credential_ref.user_credential_id

                                    if(reply_de_serialized.is_valid()):
                                        reply_de_serialized.save()

                                        data_returned['return'] = True
                                        data_returned['code'] = 100
                                        data_returned['data'] = {"reply" : reply_de_serialized.data['reply_id']}
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = f"ERROR-Serialize-{reply_de_serialized.errors}"
                                        return JsonResponse(data_returned, safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                reply_ids = tuple(set(incoming_data['reply_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    data_returned['data'] = dict()
                                    temp = dict()

                                    for id in reply_ids:
                                        try:
                                            reply_ref = Reply.objects.filter(reply_id = int(id))
                                        
                                        except Exception as ex:
                                            temp['return'] = False
                                            temp['code'] = 408
                                            temp['message'] = f"ERROR-DataType-{str(ex)}"
                                            data_returned['data'][id] = temp.copy()
                                            temp.clear()
                                        
                                        else:
                                            if(len(reply_ref) < 1):
                                                temp['return'] = False
                                                temp['code'] = 114
                                                temp['message'] = "ERROR-Invalid-Reply Id"
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                            
                                            else:
                                                reply_ref = reply_ref[0]
                                                reply_serialized = Reply_Serializer(reply_ref, many = False).data
                                                
                                                temp['return'] = True
                                                temp['code'] = 100
                                                temp['data'] = reply_serialized
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                    
                                return JsonResponse(data_returned, safe=True)
                        
                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                reply_ids = tuple(set(incoming_data['reply_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    data_returned['data'] = dict()
                                    temp = dict()

                                    for id in reply_ids:
                                        try:
                                            reply_ref = Reply.objects.filter(reply_id = int(id))
                                        
                                        except Exception as ex:
                                            temp['return'] = False
                                            temp['code'] = 408
                                            temp['message'] = f"ERROR-DataType-{str(ex)}"
                                            data_returned['data'][id] = temp.copy()
                                            temp.clear()
                                        
                                        else:
                                            if(len(reply_ref) < 1):
                                                temp['return'] = False
                                                temp['code'] = 404
                                                temp['message'] = "ERROR-Invalid-Reply Id"
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                            
                                            else:
                                                reply_ref = reply_ref[0]
                                                reply_ref.delete()
                                                
                                                temp['return'] = True
                                                temp['code'] = 100
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                    
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

                                    try:
                                        reply_ref = Reply.objects.filter(user_credential_id = user_credential_ref.user_credential_id,
                                                                         reply_id = int(incoming_data['reply_id']))

                                    except Exception as ex:
                                        data_returned['return'] = False
                                        data_returned['code'] = 408
                                        data_returned['message'] = f"ERROR-DataType-{str(ex)}"
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        if(len(reply_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = 'ERROR-Invalid-Reply does not belong to USER'
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            reply_ref = reply_ref[0]
                                            reply_de_serialized = Reply_Serializer(reply_ref, data = incoming_data)

                                            if(reply_de_serialized.is_valid()):
                                                reply_de_serialized.save()

                                                data_returned['return'] = True
                                                data_returned['code'] = 100
                                                data_returned['message'] = {"reply" : reply_de_serialized.data['reply_id']}
                                                return JsonResponse(data_returned, safe=True)
                                    
                                            else:
                                                data_returned['return'] = False
                                                data_returned['code'] = 403
                                                data_returned['message'] = f"ERROR-Serialize-{reply_de_serialized.errors}"
                                                return JsonResponse(data_returned, safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "ERROR-Action-Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = f"ERROR-Parsing-{str(ex)}"
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "ERROR-Action-Parent action invalid"
        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def lecture_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = 'ERROR-Invalid-GET Not supported'
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = f"ERROR-Parsing-{str(ex)}"
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = f"ERROR-Api-{data[1]}"
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:

                        if(incoming_data["action"].upper() == "CREATE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user") # only coordinator can add lectures

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = 'ERROR-Invalid-USER not COORDINATOR'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        # coordinator_ref = coordinator_ref[0]
                                        lecture_de_serialized = Lecture_Serializer(data = incoming_data)
                                        if(lecture_de_serialized.is_valid()):
                                            lecture_de_serialized.save()

                                            data_returned['return'] = True
                                            data_returned['code'] = 100
                                            data_returned['data'] = {"lecture" : lecture_de_serialized.data['lecture_id']}
                                        
                                        else:
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = f"ERROR-Serialise-{lecture_de_serialized.errors}"
                                            return JsonResponse(data_returned, safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                lecture_ids = tuple(set(incoming_data['lecture_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    if(len(lecture_ids) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 151
                                        data_returned['message'] = 'ERROR-Empty-Atleast one id required'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        data_returned['data'] = dict()
                                        temp = dict()

                                        for id in lecture_ids:
                                            try:
                                                lecture_ref = Lecture.objects.filter(lecture_id = int(id))
                                            
                                            except Exception as ex:
                                                temp['return'] = False
                                                temp['code'] = 408
                                                temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                            
                                            else:
                                                if(len(lecture_ref) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 404
                                                    temp['message'] = "ERROR-Invalid-Lecture ID"
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()
                                                
                                                else:
                                                    lecture_ref = lecture_ref[0]
                                                    lecture_serialized = Lecture_Serializer(lecture_ref, many=False).data

                                                    temp['return'] = True
                                                    temp['code'] = 100
                                                    temp['data'] = lecture_serialized
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()

                                return JsonResponse(data_returned, safe=True)
                        
                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                lecture_ids = tuple(set(incoming_data['lecture_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    data_returned['data'] = dict()
                                    temp = dict()

                                    for id in lecture_ids:
                                        try:
                                            lecture_ref = Lecture.objects.filter(lecture_id = int(id))
                                        
                                        except Exception as ex:
                                            temp['return'] = False
                                            temp['code'] = 408
                                            temp['message'] = f"ERROR-DataType-{str(ex)}"
                                            data_returned['data'][id] = temp.copy()
                                            temp.clear()
                                        
                                        else:
                                            if(len(lecture_ref) < 1):
                                                temp['return'] = False
                                                temp['code'] = 404
                                                temp['message'] = "ERROR-Invalid-Reply Id"
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                            
                                            else:
                                                lecture_ref = lecture_ref[0]
                                                lecture_ref.delete()
                                                
                                                temp['return'] = True
                                                temp['code'] = 100
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                    
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    # user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

                                    try:
                                        lecture_ref = Lecture.objects.filter(lecture_id = int(incoming_data['lecture_id']))

                                    except Exception as ex:
                                        data_returned['return'] = False
                                        data_returned['code'] = 408
                                        data_returned['message'] = f"ERROR-DataType-{str(ex)}"
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        if(len(lecture_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = 'ERROR-Invalid-Lecture Id'
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            lecture_ref = lecture_ref[0]
                                            lecture_de_serialized = Lecture_Serializer(lecture_ref, data = incoming_data)

                                            if(lecture_de_serialized.is_valid()):
                                                lecture_de_serialized.save()

                                                data_returned['return'] = True
                                                data_returned['code'] = 100
                                                data_returned['data'] = {"lecture" : lecture_de_serialized.data['lecture_id']}
                                                return JsonResponse(data_returned, safe=True)
                                    
                                            else:
                                                data_returned['return'] = False
                                                data_returned['code'] = 404
                                                data_returned['message'] = f"ERROR-Parsing-{lecture_de_serialized.errors}"
                                                return JsonResponse(data_returned, safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "ERROR-Action-Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = f"ERROR-Ambiguous-{str(ex)}"
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "ERROR-Action-Parent action invalid"
        return JsonResponse(data_returned, safe=True)

@csrf_exempt
def assignment_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = 'ERROR-Invalid-GET Not supported'
        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = f"ERROR-Parsing-{str(ex)}"
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = f"ERROR-Api-{data[1]}"
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:

                        if(incoming_data["action"].upper() == "CREATE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = 'ERROR-Invalid-USER not COORDINATOR'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        # coordinator_ref = coordinator_ref[0]
                                        assignment_de_serialized = Assignment_Serializer(data = incoming_data)

                                        if(assignment_de_serialized.is_valid()):
                                            assignment_de_serialized.save()

                                            data_returned['return'] = True
                                            data_returned['code'] = 100
                                            data_returned['data'] = {"assignment" : assignment_de_serialized.data['assignment_id']}
                                        
                                        else:
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = f"ERROR-Parsing-{assignment_de_serialized.errors}"
                                            return JsonResponse(data_returned, safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                assignment_ids = tuple(set(incoming_data['assignment_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 404
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    if(len(assignment_ids) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 151
                                        data_returned['message'] = 'ERROR-Empty-Atleast one id required'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        data_returned['data'] = dict()
                                        temp = dict()

                                        for id in assignment_ids:
                                            try:
                                                assignment_ref = Assignment.objects.filter(assignment_id = int(id))
                                            
                                            except Exception as ex:
                                                temp['return'] = False
                                                temp['code'] = 408
                                                temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                            
                                            else:
                                                if(len(assignment_ref) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 404
                                                    temp['message'] = "ERROR-Invalid-Assignment id."
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()
                                                
                                                else:
                                                    assignment_ref = assignment_ref[0]
                                                    assignment_serialized = Assignment_Serializer(assignment_ref, many=False).data

                                                    temp['return'] = True
                                                    temp['code'] = 100
                                                    temp['data'] = assignment_serialized
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()

                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    # user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

                                    try:
                                        assignment_ref = Assignment.objects.filter(assignment_id = int(incoming_data['assignment_id']))

                                    except Exception as ex:
                                        data_returned['return'] = False
                                        data_returned['code'] = 408
                                        data_returned['message'] = f"ERROR-DataType-{str(ex)}"
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        if(len(assignment_ref) < 1):
                                            data_returned['return'] = False
                                            data_returned['code'] = 404
                                            data_returned['message'] = 'ERROR-Invalid-Assignment Id'
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            assignment_ref = assignment_ref[0]
                                            assignment_de_serialized = Assignment_Serializer(assignment_ref, data = incoming_data)

                                            if(assignment_de_serialized.is_valid()):
                                                assignment_de_serialized.save()

                                                data_returned['return'] = True
                                                data_returned['code'] = 100
                                                data_returned['data'] = {"assignment" : assignment_de_serialized.data['assignment_id']}
                                                return JsonResponse(data_returned, safe=True)
                                    
                                            else:
                                                data_returned['return'] = False
                                                data_returned['code'] = 404
                                                data_returned['message'] = f"ERROR-Parsing-{assignment_de_serialized.errors}"
                                                return JsonResponse(data_returned, safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                assignment_ids = tuple(set(incoming_data['assignment_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    data_returned['data'] = dict()
                                    temp = dict()

                                    for id in assignment_ids:
                                        try:
                                            assignment_ref = Assignment.objects.filter(assignment_id = int(id))
                                        
                                        except Exception as ex:
                                            temp['return'] = False
                                            temp['code'] = 408
                                            temp['message'] = f"ERROR-DataType-{str(ex)}"
                                            data_returned['data'][id] = temp.copy()
                                            temp.clear()
                                        
                                        else:
                                            if(len(assignment_ref) < 1):
                                                temp['return'] = False
                                                temp['code'] = 404
                                                temp['message'] = "ERROR-Invalid-Reply Id"
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                            
                                            else:
                                                assignment_ref = assignment_ref[0]
                                                assignment_ref.delete()
                                                
                                                temp['return'] = True
                                                temp['code'] = 100
                                                data_returned['data'][id] = temp.copy()
                                                temp.clear()
                                    
                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "ERROR-Action-Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = f"ERROR-Ambiguous-{str(ex)}"
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "ERROR-Action-Parent action invalid"
        return JsonResponse(data_returned, safe=True)       

# ------------------------------------------------------------------------------------------------------------

@csrf_exempt
def post_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        post_ref_all = Post.objects.all().exclude(prime=True).order_by('-post_id')
        if(len(post_ref_all) < 1):
            data_returned['return'] = False
            data_returned['code'] = 151
            data_returned['message'] = "ERROR-Empty-Post tray"
            return JsonResponse(data_returned, safe=True)
        
        else:
            post_serialized = Post_Serializer(data = post_ref_all, many=True).data
            
            data_returned['return'] = True
            data_returned['code'] = 100
            data_returned['data'] = post_serialized

        return JsonResponse(data_returned, safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            data_returned['return'] = False
            data_returned['code'] = 401
            data_returned['message'] = f"ERROR-Parsing-{str(ex)}"
            return JsonResponse(data_returned, safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                data_returned['return'] = False
                data_returned['code'] = 402
                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                return JsonResponse(data_returned, safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    data_returned['return'] = False
                    data_returned['code'] = 150
                    data_returned['message'] = f"ERROR-Api-{data[1]}"
                    return JsonResponse(data_returned, safe=True)

                else:
                    try:
                        if(incoming_data["action"].upper() == "CREATE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = 'ERROR-Invalid-USER not COORDINATOR'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        post_de_serialized = Post_Serializer(data = incoming_data)
                                        post_de_serialized.initial_data['user_credential_id'] = int(data[1])
                                        
                                        if(post_de_serialized.is_valid()):
                                            post_de_serialized.save()

                                            data_returned['return'] = True
                                            data_returned['code'] = 100
                                            data_returned['data'] = {"post" : post_de_serialized.data['post_id']}
                                        
                                        else:
                                            data_returned['return'] = False
                                            data_returned['code'] = 403
                                            data_returned['message'] = f'ERROR-Serialize-{post_de_serialized.errors}'
                                            return JsonResponse(data_returned, safe=True)
                            
                            return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 402
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                                    if(len(coordinator_ref) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 404
                                        data_returned['message'] = 'ERROR-Invalid-USER not COORDINATOR'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        try:
                                            post_ref_self = Post.objects.filter(post_id = int(incoming_data['post_id']))
                                        
                                        except Exception as ex:
                                            data_returned['return'] = False
                                            data_returned['code'] = 403
                                            data_returned['message'] = f'ERROR-DataType-{str(ex)}'
                                            return JsonResponse(data_returned, safe=True)
                                        
                                        else:
                                            if(len(post_ref_self) < 1):
                                                data_returned['return'] = False
                                                data_returned['code'] = 403
                                                data_returned['message'] = f'ERROR-Invalid-POST id'
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                post_ref_self = post_ref_self[0]
                                                if(post_ref_self.user_credential_id != int(data[1])):
                                                    data_returned['return'] = False
                                                    data_returned['code'] = 403
                                                    data_returned['message'] = f'ERROR-Ambiguous-USER <=> POST not authorized'
                                                    return JsonResponse(data_returned, safe=True)
                                                
                                                else:
                                                    post_de_serialized = Post_Serializer(post_ref_self, data = incoming_data)
                                        
                                                    if(post_de_serialized.is_valid()):
                                                        post_de_serialized.save()

                                                        data_returned['return'] = True
                                                        data_returned['code'] = 100
                                                        data_returned['data'] = {"post" : post_de_serialized.data['post_id']}
                                                    
                                                    else:
                                                        data_returned['return'] = False
                                                        data_returned['code'] = 403
                                                        data_returned['message'] = f'ERROR-Serialize-{post_de_serialized.errors}'
                                                        return JsonResponse(data_returned, safe=True)
                            
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                post_ids = tuple(set(incoming_data['post_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 404
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    if(len(post_ids) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 151
                                        data_returned['message'] = 'ERROR-Empty-Atleast one id required'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        data_returned['data'] = dict()
                                        temp = dict()

                                        if(0 not in post_ids): # selective fetch
                                            for id in post_ids:
                                                try:
                                                    post_ref = Post.objects.filter(post_id = int(id))
                                                
                                                except Exception as ex:
                                                    temp['return'] = False
                                                    temp['code'] = 408
                                                    temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()
                                                
                                                else:
                                                    if(len(post_ref) < 1):
                                                        temp['return'] = False
                                                        temp['code'] = 404
                                                        temp['message'] = "ERROR-Invalid-Assignment id."
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                                    
                                                    else:
                                                        post_ref = post_ref[0]
                                                        post_serialized = Post_Serializer(post_ref, many=False).data

                                                        temp['return'] = True
                                                        temp['code'] = 100
                                                        temp['data'] = post_serialized
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                        
                                        else: # fetch all
                                            post_ref = Post.objects.all().order_by('-post_id')

                                            if(len(post_ref) < 1):
                                                temp['return'] = False
                                                temp['code'] = 151
                                                temp['message'] = "ERROR-Empty-Post Tray"
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()
                                                return JsonResponse(data_returned, safe=True)
                                            
                                            else:
                                                post_serialized = Post_Serializer(post_ref, many=True).data
                                                temp['return'] = True
                                                temp['code'] = 100
                                                temp['data'] = post_serialized
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()

                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                post_ids = tuple(set(incoming_data['post_id']))

                            except Exception as ex:
                                data_returned['return'] = False
                                data_returned['code'] = 404
                                data_returned['message'] = f"ERROR-Key-{str(ex)}"
                                return JsonResponse(data_returned, safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    data_returned['return'] = False
                                    data_returned['code'] = 102
                                    data_returned['message'] = 'ERROR-Hash-not USER'
                                    return JsonResponse(data_returned, safe=True)
                                
                                else:
                                    if(len(post_ids) < 1):
                                        data_returned['return'] = False
                                        data_returned['code'] = 151
                                        data_returned['message'] = 'ERROR-Empty-Atleast one id required'
                                        return JsonResponse(data_returned, safe=True)
                                    
                                    else:
                                        data_returned['data'] = dict()
                                        temp = dict()

                                        if(0 not in post_ids): # selective fetch only to be done to self or by prime_admin
                                            for id in post_ids:
                                                try:
                                                    post_ref = Post.objects.filter(post_id = int(id))
                                                
                                                except Exception as ex:
                                                    temp['return'] = False
                                                    temp['code'] = 408
                                                    temp['message'] = f"ERROR-DataType-{str(ex)}"
                                                    data_returned['data'][id] = temp.copy()
                                                    temp.clear()
                                                
                                                else:
                                                    if(len(post_ref) < 1):
                                                        temp['return'] = False
                                                        temp['code'] = 404
                                                        temp['message'] = "ERROR-Invalid-Assignment id."
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                                    
                                                    else:
                                                        post_ref = post_ref[0]
                                                        if(post_ref.user_credential_id == int(data[1])):
                                                            pass
                                                        else:
                                                            data = auth.check_authorization("admin", "prime")
                                                            if(data[0] == True):
                                                                pass
                                                            else:
                                                                temp['return'] = False
                                                                temp['code'] = 404
                                                                temp['message'] = "ERROR-Hash-not ADMIN PRIME"
                                                                data_returned['data'][id] = temp.copy()
                                                                temp.clear()

                                                        if(post_ref.video_id not in (None,"")):
                                                            post_ref.video_id.delete() # more here on video operations
                                                        if(post_ref.forum_id not in (None,"")):
                                                            post_ref.forum_id.delete()
                                                        if(post_ref.lecture_id not in (None,"")):
                                                            post_ref.lecture_id.delete()
                                                        if(post_ref.assignment_id not in (None,"")):
                                                            post_ref.assignment_id.delete()
                                                        
                                                        post_ref.delete()
                                                        
                                                        temp['return'] = True
                                                        temp['code'] = 100
                                                        data_returned['data'][id] = temp.copy()
                                                        temp.clear()
                                        
                                        else: # delete all only by prime_admin
                                            data = auth.check_authorization("admin", "prime")
                                            if(data[0] == True):
                                                post_ref = Post.objects.all().order_by('-post_id')

                                                if(len(post_ref) < 1):
                                                    temp['return'] = False
                                                    temp['code'] = 151
                                                    temp['message'] = "ERROR-Empty-Post Tray"
                                                    data_returned['data'][0] = temp.copy()
                                                    temp.clear()
                                                    return JsonResponse(data_returned, safe=True)
                                                
                                                else:
                                                    post_serialized = Post_Serializer(post_ref, many=True).data
                                                    temp['return'] = True
                                                    temp['code'] = 100
                                                    temp['data'] = post_serialized
                                                    data_returned['data'][0] = temp.copy()
                                                    temp.clear()

                                            else:
                                                temp['return'] = False
                                                temp['code'] = 404
                                                temp['message'] = "ERROR-Hash-not ADMIN PRIME"
                                                data_returned['data'][0] = temp.copy()
                                                temp.clear()
                                                return JsonResponse(data_returned, safe=True)

                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "ERROR-Action-Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        data_returned['return'] = False
                        data_returned['code'] = 404
                        data_returned['message'] = f"ERROR-Ambiguous-{str(ex)}"
                        return JsonResponse(data_returned, safe=True)

    else:
        data_returned['return'] = False
        data_returned['code'] = 403
        data_returned['message'] = "ERROR-Action-Parent action invalid"
        return JsonResponse(data_returned, safe=True)       

# ---------------------------------------------VIEW SPACE-------------------------------------------------------
