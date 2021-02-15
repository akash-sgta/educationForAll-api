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

    if(request.method == 'POST'):

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