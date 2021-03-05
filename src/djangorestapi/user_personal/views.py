from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from datetime import datetime

# ------------------------------------------------------------

from auth_prime.important_modules import CUSTOM_FALSE
from auth_prime.important_modules import INVALID_ACTION
from auth_prime.important_modules import AMBIGUOUS_404
from auth_prime.important_modules import API_RELATED
from auth_prime.important_modules import MISSING_KEY
from auth_prime.important_modules import JSON_PARSER_ERROR
from auth_prime.important_modules import GET_INVALID
from auth_prime.important_modules import TRUE_CALL

# ------------------------------------------------------------

from user_personal.models import Diary
from user_personal.models import Submission

from user_personal.serializer import Diary_Serializer
from user_personal.serializer import Submission_Serializer

from auth_prime.models import User_Credential

from content_delivery.models import Post
from content_delivery.models import Coordinator

from auth_prime.authorize import Authorize

# ------------------------------------------------------------

auth = Authorize()

# ------------------------------------------------------------

@csrf_exempt
def diary_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        return JsonResponse(GET_INVALID(), safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            return JsonResponse(JSON_PARSER_ERROR(ex), safe=True)

        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                return JsonResponse(MISSING_KEY(ex), safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    return JsonResponse(API_RELATED(data[1]), safe=True)

                else:
                    try:

                        if(incoming_data["action"].upper() == "CREATE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                return JsonResponse(MISSING_KEY(ex), safe=True)
                    
                            else:
                                data = auth.check_authorization("user")

                                if(data[0] == False):
                                    return JsonResponse(CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
                                else:
                                    diary_de_serialized = Diary_Serializer(data = incoming_data)
                                    
                                    diary_de_serialized.initial_data['user_credential_id'] = int(data[1])
                                    diary_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

                                    if(diary_de_serialized.is_valid()):
                                        diary_de_serialized.save()
                                        data_returned = TRUE_CALL(data = {"diary" : diary_de_serialized.data['diary_id'], "post" : diary_de_serialized.data['diary_id']})
                                        
                                    else:
                                        return JsonResponse(CUSTOM_FALSE(404, f"Serialise-{diary_de_serialized.errors}"), safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                datas = tuple(incoming_data['data'])

                            except Exception as ex:
                                return JsonResponse(MISSING_KEY(ex), safe=True)
                    
                            else:
                                keys = ('post_id', 'user')
                                for check in datas:
                                    if('post_id' in check.keys()):
                                        if('user_id' in check.keys()):
                                            if(check['user_id'].upper() == 'ALL'):
                                                action = 1 # all diaries of post
                                            elif(check['user_id'].upper() == 'SELF'):
                                                action = 2 # one user diaries of post+user
                                            else:
                                                action = 4
                                        else:
                                            action = 4
                                    elif('diary_id' in check.keys()):
                                        action = 3 # specific diaries
                                    else:
                                        action = 4 # invalid
                                    
                                    if(action == 4): # invalid
                                        key = "-".join(list(check.keys()))
                                        data_returned['data'][key] = MISSING_KEY('Follow API contract')
                                    
                                    elif(action == 3): # specific diaries
                                        key = "diary"
                                        data = auth.check_authorization('user')
                                        
                                        if(data[0] == False):
                                            data_returned['data'][key] = CUSTOM_FALSE(666, "Hash-not USER")
                                        
                                        else:
                                            try:
                                                diary_ids = tuple(set(check['diary_id']))
                                            
                                            except Exception as ex:
                                                data_returned['data'][key] = AMBIGUOUS_404(ex)
                                            
                                            else:
                                                for id in diary_ids:
                                                    try:
                                                        diary_ref = Diary.objects.filter(diary_id = int(id))
                                                
                                                    except Exception as ex:
                                                        data_returned['data'][key][id] = CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                                                    else:
                                                        if(len(diary_ref) < 1):
                                                            data_returned['data'][key][id] = CUSTOM_FALSE(404, "Invalid-Diary ID")
                                                    
                                                        else:
                                                            diary_ref = diary_ref[0]
                                                            if(diary_ref.user_credential_id != int(data[1])):
                                                                data_returned['data'][key][id] = CUSTOM_FALSE(404, "Invalid-Diary Does not belong to USER")

                                                            else:
                                                                diary_serialized = Diary_Serializer(diary_ref, many=False).data
                                                                data_returned['data'][key][id] = TRUE_CALL(data = diary_serialized)
                                    
                                    elif(action == 1): # all diaries of post
                                        key = "-".join('POST', check['post_id'], "ALL")
                                        data = auth.check_authorization('admin', 'alpha')

                                        if(data[1] == False):
                                            data_returned['data'][key] = CUSTOM_FALSE(666, "Hash-not ADMIN_ALPHA")
                                        
                                        else:
                                            try:
                                                diary_ref_post = Diary.objects.filter(post_id = int(check[keys[1]])).order_by("-diary_id")
                                            
                                            except Exception as ex:
                                                data_returned['data'][key] = CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                                            
                                            else:
                                                if(len(diary_ref_post) < 1):
                                                    data_returned['data'][key] = CUSTOM_FALSE(151, f"Empty-Post_Diary Tray empty")
                                                
                                                else:
                                                    diary_ref_post_serialized = Diary_Serializer(diary_ref_post, many=True).data
                                                    data_returned['data'][key] = TRUE_CALL(data = diary_ref_post_serialized)
                                    
                                    else: # one user diaries of post+user
                                        key = "-".join('POST', check['post_id'], "SELF")
                                        data = auth.check_authorization('user')

                                        if(data[1] == False):
                                            data_returned['data'][key] = CUSTOM_FALSE(666, "Hash-not USER")
                                        
                                        else:
                                            try:
                                                diary_ref_user = Diary.objects.filter(user_id = int(data[1]), post_id = int(check['post_id'])).order_by("-diary_id")
                                            
                                            except Exception as ex:
                                                data_returned['data'][key] = CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                                            
                                            else:
                                                if(len(diary_ref_user) < 1):
                                                    data_returned['data'][key] = CUSTOM_FALSE(151, f"Empty-Post_Diary Tray empty")
                                                
                                                else:
                                                    diary_ref_user_serialized = Diary_Serializer(diary_ref_user, many=True).data
                                                    data_returned['data'][key] = TRUE_CALL(data = diary_ref_post_serialized)


                                return JsonResponse(data_returned, safe=True)
                        
                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                diary_ids = tuple(set(incoming_data['diary_id']))

                            except Exception as ex:
                                return JsonResponse(MISSING_KEY(ex), safe=True)
                    
                            else:
                                data_a = auth.check_authorization("admin", "alpha")
                                data_u = auth.check_authorization("user")

                                for id in diary_ids:
                                    try:
                                        diary_ref = Diary.objects.filter(lecture_id = int(id))
                                        
                                    except Exception as ex:
                                        data_returned['data'][id] = CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                                    else:
                                        if(len(diary_ref) < 1):
                                            data_returned['data'][id] = CUSTOM_FALSE(404, "Invalid-Diary Id")
                                        
                                        else:
                                            if(data_u[0] == False):
                                                data_returned['data'][id] = CUSTOM_FALSE(404, "Hash-not USER")
                                            
                                            else:
                                                diary_ref = diary_ref[0]
                                                if(diary_ref.user_credential_id != int(data_u[1])):
                                                    if(data_a[0] == False):
                                                        data_returned['data'][id] = CUSTOM_FALSE(404, "Invalid-Diary does not belong to USER")
                                                
                                                    else: # deleted other as admin
                                                        diary_ref.delete()
                                                        data_returned['data'][id] = TRUE_CALL(message = "As ADMIN")
                                                
                                                else: # deleted self as user
                                                    diary_ref.delete()
                                                    data_returned['data'][id] = TRUE_CALL(message = "As USER")

                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                return JsonResponse(MISSING_KEY(ex), safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    return JsonResponse(CUSTOM_FALSE(102, 'Hash-not USER'), safe=True)
                                
                                else:
                                    # user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

                                    try:
                                        diary_ref = Diary.objects.filter(lecture_id = int(incoming_data['diary_id']))

                                    except Exception as ex:
                                        return JsonResponse(CUSTOM_FALSE(408, f"DataType-{str(ex)}"), safe=True)
                                    
                                    else:
                                        if(len(diary_ref) < 1):
                                            return JsonResponse(CUSTOM_FALSE(404, "Invalid-Diary Id"), safe=True)
                                        
                                        else:
                                            diary_ref = diary_ref[0]
                                            if(diary_ref.user_credential_id.user_credential_id != int(data[1])):
                                                data_returned = CUSTOM_FALSE(404, "Invalid-Diary does not belong to USER")
                                            
                                            else:
                                                diary_de_serialized = Diary_Serializer(diary_ref, data = incoming_data)

                                                if(diary_de_serialized.is_valid()):
                                                    diary_de_serialized.save()
                                                    data_returned = TRUE_CALL(data = {"diary" : diary_de_serialized.data['diary_id'], "post" : diary_de_serialized.data['diary_id']})
                                        
                                                else:
                                                    return JsonResponse(JSON_PARSER_ERROR(f"{diary_de_serialized.errors}"), safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        else:
                            data_returned['return'] = False
                            data_returned['code'] = 403
                            data_returned['message'] = "ERROR-Action-Child action invalid"
                            return JsonResponse(data_returned, safe=True)

                    except Exception as ex:
                        return JsonResponse(AMBIGUOUS_404(ex), safe=True)

    else:
        return JsonResponse(INVALID_ACTION('parent'), safe=True)

@csrf_exempt
def submission_API(request):
    global auth
    data_returned = dict()

    if(request.method == 'GET'):
        return JsonResponse(GET_INVALID(), safe=True)

    elif(request.method == 'POST'):
        data_returned['action'] = request.method.upper()
        auth.clear()

        try:
            user_data = JSONParser().parse(request)

        except Exception as ex:
            return JsonResponse(JSON_PARSER_ERROR(ex), safe=True)
        
        else:

            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]

            except Exception as ex:
                return JsonResponse(MISSING_KEY(ex), safe=True)
            
            else:
                auth.api = incoming_api
                data = auth.check_authorization(api_check=True)

                if(data[0] == False):
                    return JsonResponse(API_RELATED(data[1]), safe=True)

                else:
                    try:

                        if(incoming_data["action"].upper() == "CREATE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                return JsonResponse(MISSING_KEY(ex), safe=True)
                    
                            else:
                                data = auth.check_authorization("user") # user -> student

                                if(data[0] == False):
                                    return JsonResponse(CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
                                else:
                                    submission_de_serialized = Submission_Serializer(data = incoming_data)
                                    submission_de_serialized.initial_data['user_credential_id'] = int(data[1])
                                    submission_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

                                    if(submission_de_serialized.is_valid()):
                                        submission_de_serialized.save()
                                        data_returned = TRUE_CALL(data = {"submission" : submission_de_serialized.data['submission_id'], "assignment" : submission_de_serialized.data['assignment_id']})
                                        
                                    else:
                                        return JsonResponse(CUSTOM_FALSE(404, f"Serialise-{submission_de_serialized.errors}"), safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "READ"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                submission_ids = tuple(set(incoming_data['submission_id']))
                                assignment_ids = tuple(set(incoming_data['assignment_id']))

                            except Exception as ex:
                                return JsonResponse(MISSING_KEY(ex), safe=True)
                    
                            else:
                                data_u = auth.check_authorization("user")

                                if(data_u[0] == False):
                                    return JsonResponse(CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
                                else:
                                    if(len(submission_ids) < 1):
                                        return JsonResponse(CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                                    else:
                                        if(len(assignment_ids) < 1):
                                            flag = (False, False)
                                        else:
                                            flag = (True, True)

                                        data_returned['data'] = dict()
                                        temp = dict()
                                        coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data_u[1]))
                                        if(len(coordinator_ref) < 1):
                                            cor_flag = False
                                        else:
                                            coordinator_ref = coordinator_ref[0]
                                            cor_flag = True

                                        for id in submission_ids:
                                            try:
                                                submission_ref = Submission.objects.filter(submission_id = int(id))
                                            
                                            except Exception as ex:
                                                data_returned['data']['sumbission'][id] = CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                            
                                            else:
                                                if(len(submission_ref) < 1):
                                                    data_returned['data']['sumbission'][id] = CUSTOM_FALSE(404, "Invalid-Submission ID")
                                                
                                                else:
                                                    submission_ref = submission_ref[0]
                                                    if(submission_ref.user_credential_id != int(data_u[1])): # coordinator checking submission
                                                        if(cor_flag == False):
                                                            data_returned['data']['sumbission'][id] = CUSTOM_FALSE(666, "User not Coordinator")
                                                            flag[1] = False
                                                        
                                                        else:
                                                            submission_serialized = Submission_Serializer(submission_ref, many=False).data
                                                            data_returned['data']['sumbission'][id] = TRUE_CALL(data = submission_serialized)
                                                    
                                                    else: # self checking submissions
                                                        submission_serialized = Submission_Serializer(submission_ref, many=False).data
                                                        data_returned['data']['sumbission'][id] = TRUE_CALL(data = submission_serialized)

                                        if(flag[0] == False):
                                            pass
                                        else:
                                            if(flag[1] == False):
                                                data_returned['data']['assignment'] = CUSTOM_FALSE(666, "USER not COORDINATOR")
                                            else:
                                                for id in assignment_ids:
                                                    try:
                                                        post_ref = Submission.objects.filter(assignment_id = int(id))
                                            
                                                    except Exception as ex:
                                                        data_returned['data']['assignment'][id] = CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                            
                                                    else:
                                                        if(len(post_ref) < 1):
                                                            data_returned['data']['assignment'][id] = CUSTOM_FALSE(408, "Invalid-Assignment id")
                                                        
                                                        else:
                                                            post_ref = post_ref[0]
                                                            assignment_id = post_ref.assignment_id.assignment_id
                                                            submission_ref = Submission.objects.filter(assignment_id = assignment_id)

                                                            if(len(submission_ref) < 1):
                                                                data_returned['data']['assignment'][id] = CUSTOM_FALSE(151, "Empty-Assignment<=>Submission Empty")
                                                            
                                                            else:
                                                                submission_serialized = Submission_Serializer(submission_ref, many=True).data
                                                                data_returned['data']['assignment'][id] = TRUE_CALL(data = submission_serialized)

                                return JsonResponse(data_returned, safe=True)
                        
                        elif(incoming_data["action"].upper() == "DELETE"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                submission_ids = tuple(set(incoming_data['submission_id']))

                            except Exception as ex:
                                return JsonResponse(MISSING_KEY(ex), safe=True)
                    
                            else:
                                data_u = auth.check_authorization("user")

                                if(data_u[0] == False):
                                    return JsonResponse(CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
                                else:
                                    if(len(submission_ids) < 1):
                                        return JsonResponse(CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                                    else:
                                        data_returned['data'] = dict()
                                        temp = dict()
                                        coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data_u[1]))
                                        if(len(coordinator_ref) < 1):
                                            cor_flag = False
                                        else:
                                            coordinator_ref = coordinator_ref[0]
                                            cor_flag = True

                                        for id in submission_ids:
                                            try:
                                                submission_ref = Submission.objects.filter(submission_id = int(id))
                                            
                                            except Exception as ex:
                                                data_returned['data'][id] = CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                            
                                            else:
                                                if(len(submission_ref) < 1):
                                                    data_returned['data'][id] = CUSTOM_FALSE(404, "Invalid-Submission ID")
                                                
                                                else:
                                                    submission_ref = submission_ref[0]
                                                    if(submission_ref.user_credential_id != int(data_u[1])): # coordinator deleting submission ?
                                                        # if(cor_flag == False):
                                                        #     data_returned['data'][id] = CUSTOM_FALSE(666, "User not Coordinator")
                                                        #     flag[1] = False
                                                        
                                                        # else:
                                                        #     submission_ref.delete()
                                                        #     data_returned['data'][id] = TRUE_CALL()
                                                        data_returned['data'][id] = CUSTOM_FALSE(666, "NotBelong-USER<=>SUBMISSION")
                                                    
                                                    else: # self delete submissions
                                                        submission_ref.delete()
                                                        data_returned['data'][id] = TRUE_CALL()
                                    
                                return JsonResponse(data_returned, safe=True)

                        elif(incoming_data["action"].upper() == "EDIT"):
                            data_returned['action'] += "-"+incoming_data["action"].upper()
                        
                            try:
                                incoming_data = incoming_data['data']
                                auth.token = incoming_data['hash']
                                incoming_data = incoming_data['data']

                            except Exception as ex:
                                return JsonResponse(MISSING_KEY(ex), safe=True)
                    
                            else:
                                data = auth.check_authorization("user")
                                
                                if(data[0] == False):
                                    return JsonResponse(CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
                                else:
                                    # user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))

                                    try:
                                        submission_ref = Submission.objects.filter(submission_id = int(incoming_data['submission_id']))

                                    except Exception as ex:
                                        return JsonResponse(CUSTOM_FALSE(408, "DataType-{str(ex)}"), safe=True)
                                    
                                    else:
                                        if(len(submission_ref) < 1):
                                            return JsonResponse(CUSTOM_FALSE(404, "Invalid-Submission Id"), safe=True)
                                        
                                        else:
                                            submission_ref = submission_ref[0]
                                            if(submission_ref.user_credential_id != int(data[1])):
                                                return JsonResponse(CUSTOM_FALSE(404, 'Invalid-Submission does not belong to USER'), safe=True)
                                            
                                            else:
                                                submission_de_serialized = Submission_Serializer(submission_ref, data = incoming_data)

                                                if(submission_de_serialized.is_valid()):
                                                    submission_de_serialized.save()

                                                    data_returned = TRUE_CALL(data = {"submission" : submission_de_serialized.data['submission_id'], "assignment" : submission_de_serialized.data['assignment_id']})
                                        
                                                else:
                                                    return JsonResponse(JSON_PARSER_ERROR(f"{submission_de_serialized.errors}"), safe=True)
                                
                                return JsonResponse(data_returned, safe=True)

                        else:
                            return JsonResponse(INVALID_ACTION('child'), safe=True)

                    except Exception as ex:
                        return JsonResponse(AMBIGUOUS_404(ex), safe=True)

    else:
        return JsonResponse(INVALID_ACTION('parent'), safe=True)