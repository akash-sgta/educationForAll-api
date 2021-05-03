from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from auth_prime.models import (
        User_Credential,
        User_Profile
    )
from auth_prime.serializer import (
        User_Profile_Serializer
    )

# ------------------------------------------------------------

class User_Profile_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()
    
    def post(self, request, pk=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        isAuthorizedUSER = am_I_Authorized(request, "USER")
        if(isAuthorizedUSER[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
            return Response(data = data)
        else:
            data = dict()
            user_cred_ref = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
            if(user_cred_ref.user_profile_id in (None, "")):
                user_prof_serialized = User_Profile_Serializer(data=request.data)
                if(user_prof_serialized.initial_data['prime'] == True
                and user_prof_serialized.initial_data['user_roll_number'] in (None, "")):
                    data['success'] = False
                    data['message'] = "Student profile requires roll number"
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if(user_prof_serialized.is_valid()):
                        user_prof_serialized.save()

                        user_prof_ref = User_Profile.objects.get(user_profile_id = user_prof_serialized.data['user_profile_id'])
                        user_cred_ref.user_profile_id = user_prof_ref
                        user_cred_ref.save()
                        
                        data['success'] = True
                        data['data'] = user_prof_serialized.data
                        return Response(data=data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = f"error:SERIALIZING_ERROR, message:{user_prof_serialized.errors}"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['success'] = True
                data['message'] = "Profile already created"
                data['data'] = User_Profile_Serializer(user_cred_ref.user_profile_id, many=False).data
                return Response(data = data, status=status.HTTP_201_CREATED)
    
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
                    if(int(pk) == 0 or int(pk) == isAuthorizedUSER[1]): #self
                        user_cred_ref = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                        if(user_cred_ref.user_profile_id in (None, "")):
                            data['success'] = False
                            data['message'] = "User does not have profile"
                            return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                        else:
                            data['success'] = True
                            data['data'] = User_Profile_Serializer(user_cred_ref.user_profile_id, many=False).data
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        if(am_I_Authorized(request, 'ADMIN') > 0):
                            if(int(pk) == 666):
                                user_prof_ref = User_Profile.objects.all()
                                data['success'] = True
                                data['data'] = User_Profile_Serializer(user_prof_ref, many=True).data
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                            else:
                                try:
                                    user_cred_ref = User_Credential.objects.get(user_credential_id = pk)
                                except User_Credential.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = "item invalid"
                                    return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                                else:
                                    data['success'] = True
                                    data['data'] = User_Profile_Serializer(user_cred_ref.user_profile_id, many=False).data
                                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = "User does not have ADMIN privileges"
                            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/user/prof/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
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
                    user_cred_ref = User_Credential.objects.filter(user_credential_id = isAuthorizedUSER[1])
                except User_Credential.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    user_cred_ref = user_cred_ref[0]
                    user_prof_serialized = User_Profile_Serializer(user_cred_ref.user_profile_id, data=request.data)
                    if(user_prof_serialized.initial_data['prime'] == True
                    and user_prof_serialized.initial_data['user_roll_number'] in (None, "")):
                        data['success'] = False
                        data['message'] = "Student profile requires roll number"
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if(user_prof_serialized.is_valid()):
                            user_prof_serialized.save()
                            data['success'] = True
                            data['data'] = user_prof_serialized.data
                            return Response(data = data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = f"error:SERIALIZING_ERROR, message:{user_prof_serialized.errors}"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/user/prof/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
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
                    if(int(pk) == 0 or int(pk) == isAuthorizedUSER[1]): #self
                        usr = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                        if(usr.user_profile_id == None):
                            data['success'] = True
                            data['message'] = "User Profile Not found"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            usr.user_profile_id.delete()
                            data['success'] = True
                            data['message'] = "User Profile Deleted"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        isAuthorizedADMIN = am_I_Authorized(request, 'ADMIN')
                        if(isAuthorizedADMIN > 0):
                            if(int(pk) == 666):
                                User_Profile.objects.all().delete()
                                data['success'] = True
                                data['message'] = "All User Profile(s) Deleted"
                                return Response(data = data, status = status.HTTP_202_ACCEPTED)
                            else:
                                try:
                                    user_cred_ref = User_Credential.objects.get(user_credential_id = pk)
                                except User_Credential.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = "item invalid"
                                    return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                                else:
                                    if(user_cred_ref.user_profile_id == None):
                                        data['success'] = True
                                        data['message'] = "User Profile Not found"
                                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                                    else:
                                        usr.user_profile_id.delete()
                                        data['success'] = True
                                        data['message'] = "User Profile Deleted by ADMIN"
                                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            data['success'] = False
                            data['message'] = "User does not have ADMIN privileges"
                            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                except Exception as ex:
                    print("EX : ", ex)
                    return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/user/prof/<id>'
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
        
        data["name"] = "User_Profile"
        
        temp["POST"] = {
                "user_profile_headline" : "String",
                "user_bio" : "String",
                "user_english_efficiency" : "Number(1/2/3)",
                "user_git_profile" : "URL",
                "user_profile_pic" : "Number/null",
                "user_likedin_profile" : "URL",
                "user_roll_number" : "Number(14 digit)",
                "prime" : "Boolean"
            }
        temp["GET"] = None
        temp["PUT"] = {
                "user_profile_headline" : "String",
                "user_bio" : "String",
                "user_english_efficiency" : "Number(1/2/3)",
                "user_git_profile" : "URL",
                "user_profile_pic" : "Number/null",
                "user_likedin_profile" : "URL",
                "user_roll_number" : "Number(14 digit)",
                "prime" : "Boolean"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)


