from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
        create_password_hashed,
        create_token
    )

from auth_prime.models import (
        User_Credential,
        User_Profile,
        User_Token_Table,
        Image
    )
from auth_prime.serializer import (
        User_Credential_Serializer
    )

# ------------------------------------------------------------

class User_Credential_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()
    
    def post(self, request, pk=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        isAuthorizedUSER = am_I_Authorized(request, "USER")
        if(request.data['action'].lower() == 'signin'): # TODO : If user is already signed in through cache [x]don't let signin again
            if(isAuthorizedUSER[0]):
                user_cred_ref = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                user_cred_serialized = User_Credential_Serializer(user_cred_ref, many=False)
                data['success'] = False
                data['message'] = "USER_ALREADY_LOGGED_IN"
                return Response(data = data, status=status.HTTP_201_CREATED)
            else:
                myData = request.data['data']
                user_cred_ref = User_Credential.objects.filter(user_email = myData['email'].lower())
                if(len(user_cred_ref) < 1):
                    data['success'] = False
                    data['message'] = "EMAIL_NOT_REGISTERED"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    user_cred_ref = user_cred_ref[0]
                    if(user_cred_ref.user_password != create_password_hashed(myData['password'])):
                        data['success'] = False
                        data['message'] = "PASSWORD_INCORRECT"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        data['success'] = True
                        data['data'] = {
                                "JWT" : create_token(user_cred_ref)
                            }
                        return Response(data = data, status=status.HTTP_201_CREATED)
        
        elif(request.data['action'].lower() == 'signup'):
            if(isAuthorizedUSER[0]): # TODO : If user is already signed in through cache [x]don't let signin again
                data['success'] = False
                data['message'] = "USER_ALREADY_LOGGED_IN"
                return Response(data = data, status=status.HTTP_403_FORBIDDEN)
            else:
                user_cred_de_serialized = User_Credential_Serializer(data = request.data['data'])
                user_cred_de_serialized.initial_data['user_email'] = user_cred_de_serialized.initial_data['user_email'].lower()
                if(len(User_Credential.objects.filter(user_email = user_cred_de_serialized.initial_data['user_email'])) > 0):
                    data['success'] = False
                    data['message'] = "EMAIL_ALREADY_REGISTERED"
                    return Response(data = data, status = status.HTTP_403_FORBIDDEN)
                else:
                    user_cred_de_serialized.initial_data['user_password'] = create_password_hashed(user_cred_de_serialized.initial_data['user_password'])
                    if(user_cred_de_serialized.is_valid()):
                        user_cred_de_serialized.save()
                        data['success'] = True
                        user_cred_ref = User_Credential.objects.get(user_credential_id = user_cred_de_serialized.data['user_credential_id'])
                        data['data'] = {
                                "JWT" : create_token(user_cred_ref),
                                "cred" : user_cred_de_serialized.data
                            }
                        data['data']['cred']['user_password'] = "■ ■ ■ ■ ■ ■ ■"
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = user_cred_de_serialized.errors
                        return Response(data = data, status = status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)

        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data)
            else:
                try:
                    if(int(pk) == 0): # TODO : User asking to read own credentials
                        user_cred_ref = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                        data['success'] = True
                        data['data'] = User_Credential_Serializer(user_cred_ref, many=False).data
                        data['data']['user_password'] = "■ ■ ■ ■ ■ ■ ■"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    elif(int(pk) == 87795962440396049328460600526719): # TODO : ADMIN asking to read everyone's cred
                        isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                        if(isAuthorizedADMIN > 0):
                            user_cred_ref = User_Credential.objects.all()
                            data['success'] = True
                            data['data'] = User_Credential_Serializer(user_cred_ref, many=True).data
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = "USER_NOT_ADMIN"
                            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                    else: # TODO : ADMIN asking to read indivisual select user cred
                        isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                        if(isAuthorizedADMIN > 0):
                            try:
                                user_cred_ref = User_Credential.objects.get(user_credential_id = pk)
                            except User_Credential.DoesNotExist:
                                data['success'] = False
                                data['message'] = "USER_ID_INVALID"
                                return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                            else:
                                data['success'] = True
                                data['data'] = User_Credential_Serializer(user_cred_ref, many=False).data
                                data['data']['user_password'] = "■ ■ ■ ■ ■ ■ ■"
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = "USER_NOT_ADMIN"
                            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/user/cred/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None): # FIXME : Add admin access to change password of users
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)

        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"USER_NOT_AUTHORIZED"
                return Response(data = data)
            else:
                try:
                    user_cred_ref = User_Credential.objects.filter(user_credential_id = isAuthorizedUSER[1])
                except User_Credential.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    user_cred_ref = user_cred_ref[0]
                    user_cred_serialized = User_Credential_Serializer(user_cred_ref, data=request.data)
                    user_cred_serialized.initial_data['user_credential_id'] = isAuthorizedUSER[1]
                    test_ref = User_Credential.objects.filter(user_email = user_cred_serialized.initial_data['user_email'].lower())
                    if(len(test_ref) > 0 and test_ref[0].user_credential_id != isAuthorizedUSER[1]):
                        data['success'] = False
                        data['message'] = "EMAIL_ALREADY_REGISTERED"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if(user_cred_serialized.is_valid()):
                            user_cred_serialized.save()
                            data['success'] = True
                            data['data'] = user_cred_serialized.data
                            return Response(data = data)
                        else:
                            data['success'] = False
                            data['message'] = f"SERIALIZING_ERROR : {user_cred_serialized.errors}"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/user/cred/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"USER_NOT_AUTHORIZED"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    if(int(pk) == 0): # TODO : User cred delete
                        user_cred_ref = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                        if(user_cred_ref.user_profile_id != None):
                            if(user_cred_ref.user_profile_id.user_profile_pic != None):
                                user_cred_ref.user_profile_id.user_profile_pic.delete()
                            user_cred_ref.user_profile_id.delete()
                        user_cred_ref.delete()
                        data['success'] = True
                        data['message'] = "USER_DELETED"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    elif(int(pk) == 87795962440396049328460600526719): # TODO : User logout
                        try:
                            user_token_ref = User_Token_Table.objects.get(user_credential_id = isAuthorizedUSER[1])
                        except User_Token_Table.DoesNotExist:
                            data['success'] = True
                            data['message'] = "USER_ALREADY_LOGGED_OUT"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            user_token_ref.delete()
                            data['success'] = True
                            data['message'] = "USER_LOGGED_OUT"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    elif(int(pk) == 13416989436929794359012690353783): # TODO : ADMIN delete all user cred
                        if(am_I_Authorized(request, 'ADMIN') > 0):
                            User_Credential.objects.all().exclude(user_credential_id = isAuthorizedUSER[1]).delete() # delete all cred excluding admin's
                            user_cred = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                            if(user_cred.user_profile_id != None): # delete all prof excluding admin's
                                User_Profile.objects.all().exclude(user_profile_id = user_cred.user_profile_id.user_profile_id).delete()
                            data['success'] = True
                            data['message'] = "ADMIN : All_USER_DELETED"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = "USER_NOT_ADMIN"
                            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                    else: # TODO : Admin deletes selected user
                        if(am_I_Authorized(request, 'ADMIN') > 0):
                            try:
                                user_cred_ref = User_Credential.objects.get(user_credential_id = pk)
                            except User_Credential.DoesNotExist:
                                data['success'] = False
                                data['message'] = "USER_ID_INVALID"
                                return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                            else:
                                user_cred_ref.delete()
                                data['success'] = True
                                data['message'] = "ADMIN : USER_DELETED"
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = "USER_NOT ADMIN"
                            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/user/cred/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            
        temp = dict()

        data["Allow"] = "POST GET PUT DELETE OPTIONS".split()
        
        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()
        
        data["name"] = "User_Credential"
        
        temp["POST"] = (
            {
                "action" : "signup",
                "data" : {
                    "user_f_name" : "String",
                    "user_m_name" : "String/null",
                    "user_l_name" : "String",
                    "user_email" : "Email",
                    "user_password" : "String[min 8 char]",
                    "user_security_question" : "String",
                    "user_security_answer" : "String"
                },
            },
            {
                "action" : "signin",
                "data" : {
                    "email" : "Email",
                    "password" : "String"
                }
            }
        )
        temp["GET"] = None
        temp["PUT"] = {
                "user_f_name" : "String",
                "user_m_name" : "String",
                "user_l_name" : "String",
                "user_email" : "Email",
                "user_password" : "String",
                "user_security_question" : "String",
                "user_security_answer" : "String"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
