from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from auth_prime.models import (
        Image
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
        isAuthorizedUSER = am_I_Authorized(request, "USER")
        if(isAuthorizedUSER[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if(len(request.FILES) < 1):
                data['success'] = False
                data['message'] = "No data passed to api endpoint"
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
                        data['message'] = "Image size should be less than 5MB"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data['success'] = False
                    data['message'] = "File shoud be image file"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
        data = dict()
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    image_ref = Image.objects.get(image_id = int(pk))
                except Image.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data['success'] = True
                    data['data'] = image_ref.image.url
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
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if(isAuthorizedADMIN < 3):
                    data['success'] = False
                    data['message'] = "USER does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    # create new
                    image_file = request.FILES['image']
                    if(str(image_file.content_type).startswith("image")):
                        if(image_file.size < 5000000):
                            
                            # delete old
                            try:
                                image_ref = Image.objects.get(image_id = int(pk))
                            except Image.DoesNotExist:
                                data['success'] = False
                                data['message'] = "item does not exist"
                                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                image_ref.image = image_file
                                image_ref.save()
                                data['success'] = True
                                serialized = Image_Serializer(image_ref, many=False).data
                                data['message'] = "New Image set"
                                data['data'] = serialized
                                return Response(data = data, status=status.HTTP_201_CREATED)
                        else:
                            data['success'] = False
                            data['message'] = "Image size should be less than 5MB"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data['success'] = False
                        data['message'] = "File shoud be image file"
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
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    image_ref = Image.objects.get(image_id = int(pk))
                except Image.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    image_ref.delete()
                    data['success'] = True
                    data['data'] = "Image deleted"
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/user/image/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)


