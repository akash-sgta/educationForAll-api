from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from auth_prime.models import (
        Image,
        User_Credential,
    )
from auth_prime.serializer import (
        Image_Serializer
    )

# ------------------------------------------------------------

class User_Profile_Image_View(APIView):

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
        if(isAuthorizedUSER[0] == False):
            data['success'] = False
            data['message'] = f"USER_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(len(request.FILES) < 1):
                data['success'] = False
                data['message'] = "NO_DATA_RECIEVED"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                image_file = request.FILES['image']
                if(str(image_file.content_type).startswith("image")):
                    if(image_file.size < 5000000):
                        image_ref = Image(image = image_file)
                        image_ref.save()
                        data['success'] = True
                        serialized = Image_Serializer(image_ref, many=False).data
                        data['data'] = serialized
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = False
                        data['message'] = "IMAGE_SIZE_LESS_THAN_5MB"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data['success'] = False
                    data['message'] = "FILE_SHOULD_BE_IMAGE"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
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
                if(int(pk) == 87795962440396049328460600526719): # TODO : ADMIN looking for all images
                    if(am_I_Authorized(request, "ADMIN") > 0):
                        data['success'] = True
                        data['data'] = Image_Serializer(Image.objects.all(), many=True).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = f"USER_NOT_ADMIN"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else: # TODO : User looking for specific image
                    try:
                        image_ref = Image.objects.get(image_id = int(pk))
                    except Image.DoesNotExist:
                        data['success'] = False
                        data['message'] = "IMAGE_ID_INVALID"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data['success'] = True
                        data['data'] = Image_Serializer(image_ref, many=False).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/user/image/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
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
                    image_ref = Image.objects.get(image_id = int(pk))
                except Image.DoesNotExist:
                    data['success'] = False
                    data['message'] = "IMAGE_ID_INVALID"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user_cred_ref = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                    flag = (False, "TRY_AGAIN : ")
                    if(user_cred_ref.user_profile_id != None):
                        if(user_cred_ref.user_profile_id.user_profile_pic != None):
                            if(user_cred_ref.user_profile_id.user_profile_pic.image_id == int(pk)): # TODO : User changing own picture
                                flag = (True, "")
                            else: # TODO : Admin changing any picture
                                if(am_I_Authorized(request, "ADMIN") > 0):
                                    flag = (True, "ADMIN : ")
                                else:
                                    flag = (False, "ADMIN : ")
                    
                    if(not flag[0]):
                        data['success'] = False
                        data['message'] = flag[1]+"NOT_AUTHORIZED"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # create new
                        image_file = request.FILES['image']
                        if(str(image_file.content_type).startswith("image")):
                            if(image_file.size < 5000000):                            
                                # delete old
                                try:
                                    image_ref = Image.objects.get(image_id = int(pk)) # TODO : double check because od concurrent access
                                except Image.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = flag[1]+"IMAGE_ID_INVALID"
                                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    image_ref.image = image_file
                                    image_ref.save()
                                    data['success'] = True
                                    serialized = Image_Serializer(image_ref, many=False).data
                                    data['message'] = flag[1]+"NEW_IMAGE_SET"
                                    data['data'] = serialized
                                    return Response(data = data, status=status.HTTP_201_CREATED)
                            else:
                                data['success'] = False
                                data['message'] = flag[1]+"IMAGE_SIZE_LESS_THAN_5MB"
                                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            data['success'] = False
                            data['message'] = flag[1]+"FILE_SHOULD_BE_IMAGE"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/user/image/<id>'
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
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(int(pk) == 87795962440396049328460600526719):
                    if(am_I_Authorized(request, "ADMIN") > 0):
                        Image.object.all().delete()
                        data['success'] = True
                        data['data'] = "ADMIN : ALL_IMAGES_DELETED"
                        return Response(data = data, status=status.HTTP_200_OK)
                    else:
                        data['success'] = False
                        data['message'] = f"USER_NOT_ADMIN"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    user_cred_ref = User_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                    flag = (False, "TRY_AGAIN : ")
                    if(user_cred_ref.user_profile_id != None):
                        if(user_cred_ref.user_profile_id.user_profile_pic != None):
                            if(user_cred_ref.user_profile_id.user_profile_pic.image_id == int(pk)): # TODO : User deleting own picture
                                flag = (True, "")
                            else: # TODO : Admin deleting any picture
                                if(am_I_Authorized(request, "ADMIN") > 0):
                                    flag = (True, "ADMIN : ")
                                else:
                                    flag = (False, "ADMIN : ")
                    
                    if(not flag[0]):
                        data['success'] = False
                        data['message'] = flag[1]+"NOT_AUTHORIZED"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        try:
                            image_ref = Image.objects.get(image_id = int(pk))
                        except Image.DoesNotExist:
                            data['success'] = False
                            data['message'] = flag[1]+"IMAGE_ID_INVALID"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            image_ref.delete()
                            data['success'] = True
                            data['data'] = flag[1]+"IMAGE_DELETED"
                            return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/user/image/<id>'
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
        
        temp["Content-Type"] = "multipart/form-data"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()
        
        data["name"] = "User_Profile_Image"
        
        temp["POST"] = {
            "image" : "FILE"
        }
        temp["GET"] = None
        temp["PUT"] = {
            "image" : "FILE"
        }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)

