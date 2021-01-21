from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from auth_prime.models import User_Table,Admin_Table,Token_Table
from auth_prime.serializer import User_Table_Serializer, Admin_Table_Serializer, Token_Table_Serializer

# Create your views here.

@csrf_exempt
def user_API(request, id=0):

    if(request.method == 'GET'):
        try:
            if(id == 0):
                users = User_Table.objects.all()
                users_serialized = User_Table_Serializer(users, many=True)
                return JsonResponse(users_serialized.data, safe=False)
            else:
                users = User_Table.objects.get(user_id=id)
                users_serialized = User_Table_Serializer(users, many=False)
                return JsonResponse(users_serialized.data, safe=False)
        except Exception as ex:
            print(f"[!] USER API : GET : {ex}")
            return JsonResponse("USER : [x] Data Get -> Unsuccessful.", safe=False)
    
    elif(request.method == 'POST'):
        user_data = JSONParser().parse(request)
        user_de_serialized = User_Table_Serializer(data=user_data)
        if(user_de_serialized.is_valid()):
            user_de_serialized.save()
            return JsonResponse("USER : [.] Data Add -> Successful.", safe=False)
        else:
            return JsonResponse("USER : [x] Data Add -> Unsuccessful.", safe=False)
    
    elif(request.method == 'PUT'):
        user_data = JSONParser().parse(request)
        user = User_Table.objects.get(user_id = user_data['user_id'])
        user_de_serialized = User_Table_Serializer(user, data=user_data)
        if(user_de_serialized.is_valid()):
            user_de_serialized.save()
            return JsonResponse("USER : [.] Update -> Successful.", safe=False)
        else:
            return JsonResponse("USER : [x] Update -> Unsuccessful.", safe=False)
    
    elif(request.method == 'DELETE'):
        try:
            user = User_Table.objects.get(user_id=id)
            user.delete()
        except Exception as ex:
            print(f"USER API : DELETE : {ex}")
            return JsonResponse("USER : [.] Delete -> Unsuccessful.", safe=False)
        else:
            return JsonResponse("USER : [.] Delete -> Successful.", safe=False)
    
    else:
        return JsonResponse("USER : [x] Invalid Method. (use POST/GET/PUT/DELETE)", safe=False)

@csrf_exempt
def admin_API(request, id=0):

    if(request.method == 'GET'):
        try:
            if(id == 0):
                admins = Admin_Table.objects.all()
                admins_serialized = Admin_Table_Serializer(admins, many=True)
                return JsonResponse(admins_serialized.data, safe=False)
            else:
                admins = Admin_Table.objects.get(admin_id=id)
                admins_serialized = Admin_Table_Serializer(admins, many=False)
                return JsonResponse(admins_serialized.data, safe=False)
        except Exception as ex:
            print(f"[!] ADMIN API : GET : {ex}")
            return JsonResponse("ADMIN : [x] Data Get -> Unsuccessful.", safe=False)
    
    elif(request.method == 'POST'):
        admin_data = JSONParser().parse(request)
        admin_de_serialized = Admin_Table_Serializer(data=admin_data)
        if(admin_de_serialized.is_valid()):
            admin_de_serialized.save()
            return JsonResponse("ADMIN : [.] Data Add -> Successful.", safe=False)
        else:
            return JsonResponse("ADMIN : [x] Data Add -> Unsuccessful.", safe=False)
    
    elif(request.method == 'PUT'):
        admin_data = JSONParser().parse(request)
        admin = Admin_Table.objects.get(admin_id = admin_data['admin_id'])
        admin_de_serialized = Admin_Table_Serializer(admin, data=admin_data)
        if(admin_de_serialized.is_valid()):
            admin_de_serialized.save()
            return JsonResponse("ADMIN : [.] Update -> Successful.", safe=False)
        else:
            return JsonResponse("ADMIN : [x] Update -> Unsuccessful.", safe=False)
    
    elif(request.method == 'DELETE'):
        try:
            admin = Admin_Table.objects.get(admin_id=id)
            admin.delete()
        except Exception as ex:
            print(f"[!] ADMIN API : DELETE : {ex}")
            return JsonResponse("ADMIN : [.] Delete -> Unsuccessful.", safe=False)
        else:
            return JsonResponse("ADMIN : [x] Delete -> Successful.", safe=False)
    
    else:
        return JsonResponse("[x] Invalid Method. (use POST/GET/PUT/DELETE)", safe=False)

@csrf_exempt
def token_API(request, id=0):

    if(request.method == 'GET'):
        try:
            if(id == 0):
                tokens = Token_Table.objects.all()
                tokens_serialized = Token_Table_Serializer(tokens, many=True)
                return JsonResponse(tokens_serialized.data, safe=False)
            else:
                tokens = Token_Table.objects.get(token_id=id)
                tokens_serialized = Token_Table_Serializer(tokens, many=False)
                return JsonResponse(tokens_serialized.data, safe=False)
        except Exception as ex:
            print(f"[!] ADMIN API : GET : {ex}")
            return JsonResponse("ADMIN : [x] Data Get -> Unsuccessful.", safe=False)
    
    elif(request.method == 'POST'):
        token_data = JSONParser().parse(request)
        token_de_serialized = Token_Table_Serializer(data=token_data)
        print(token_de_serialized)
        if(token_de_serialized.is_valid()):
            token_de_serialized.save()
            return JsonResponse("TOKEN : [.] Data Add -> Successful.", safe=False)
        else:
            return JsonResponse("TOKEN : [x] Data Add -> Unsuccessful.", safe=False)
    
    elif(request.method == 'PUT'):
        token_data = JSONParser().parse(request)
        token = Token_Table.objects.get(token_id = token_data['token_id'])
        token_de_serialized = Token_Table_Serializer(token, data=token_data)
        if(token_de_serialized.is_valid()):
            token_de_serialized.save()
            return JsonResponse("TOKEN : [.] Update -> Successful.", safe=False)
        else:
            return JsonResponse("TOKEN : [x] Update -> Unsuccessful.", safe=False)
    
    elif(request.method == 'DELETE'):
        try:
            token = Token_Table.objects.get(token_id=id)
            token.delete()
        except Exception as ex:
            print(f"[!] TOKEN API : DELETE : {ex}")
            return JsonResponse("TOKEN : [.] Delete -> Unsuccessful.", safe=False)
        else:
            return JsonResponse("TOKEN : [x] Delete -> Successful.", safe=False)
    
    else:
        return JsonResponse("[x] Invalid Method. (use POST/GET/PUT/DELETE)", safe=False)