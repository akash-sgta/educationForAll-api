from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from user_personal.models import Diary, Submission
from user_personal.serializer import Diary_Serializer, Submission_Serializer

from auth_prime.models import User_Credential

from content_delivery.models import Post

from auth_prime.authorize import Authorize

# Create your views here.

auth = Authorize()

@csrf_exempt
def diary_API(request):
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


        data_returned['action'] = 'POST'

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
        
        data_returned['action'] += "-"+incoming_action.upper()
        
        auth.clear()

        try:
            auth.token = incoming_data['hash']
            incoming_data = incoming_data['data']
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
            incoming_data['user_credential_id'] = user_credential_ref[0]

            post_ref = Post.objects.filter(post_id = int(incoming_data['post_id']))
            if(len(post_ref) < 1):
                data_returned['return'] = False
                data_returned['code'] = 301
            else:
                incoming_data['post_id'] = post_ref[0]
                
                try:
                    diary_de_serialized = Diary_Serializer(data=incoming_data)
                except Exception as ex:
                    data_returned['return'] = False
                    data_returned['code'] = 502
                    data_returned['message'] = str(ex)

                    return JsonResponse(data_returned, safe=True)
                
                if(diary_de_serialized.is_valid()):
                    diary_de_serialized.save()
                    
                    data_returned['return'] = True
                    data_returned['code'] = 200
                else:
                    data_returned['return'] = True
                    data_returned['code'] = 401
                    data_returned['message'] = diary_de_serialized.errors
                    
            return JsonResponse(data_returned, safe=True)