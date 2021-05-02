from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from content_delivery.models import (
        Coordinator,
        Lecture
    )
from content_delivery.serializer import (
        Lecture_Serializer
    )

# ------------------------------------------------------------

class Lecture_View(APIView):

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
            coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
            if(len(coordinator_ref) < 1):
                data['success'] = False
                data['message'] = "USER not COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                lecture_de_serialized = Lecture_Serializer(data = request.data)
                if(lecture_de_serialized.is_valid()):
                    lecture_de_serialized.save()
                    data['success'] = True
                    data['data'] = lecture_de_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = lecture_de_serialized.errors
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
                if(int(pk) == 0): #all
                    data['success'] = True
                    data['data'] = Lecture_Serializer(Lecture.objects.all(), many=True).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    try:
                        lecture_ref = Lecture.objects.get(lecture_id = int(pk))
                    except Lecture.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data['success'] = True
                        data['data'] = Lecture_Serializer(lecture_ref, many=False).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/content/lecture/<id>'
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
                coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                if(len(coordinator_ref) < 1):
                    data['success'] = False
                    data['message'] = "USER not COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        lecture_ref = Lecture.objects.get(lecture_id = int(pk))
                    except Lecture.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        lecture_de_serialized = Lecture_Serializer(lecture_ref, data=request.data)
                        if(lecture_de_serialized.is_valid()):
                            lecture_de_serialized.save()
                            data['success'] = True
                            data['data'] = lecture_de_serialized.data
                            return Response(data = data, status=status.HTTP_201_CREATED)
                        else:
                            data['success'] = False
                            data['message'] = lecture_de_serialized.errors
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/content/lecture/<id>'
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
                coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                if(len(coordinator_ref) < 1):
                    data['success'] = False
                    data['message'] = "USER not COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if(int(pk) == 0): #all
                        Lecture.objects.all().delete()
                        data['success'] = True
                        data['message'] = "All LECTURE(s) deleted"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            lecture_ref = Lecture.objects.get(lecture_id = int(pk))
                        except Lecture.DoesNotExist:
                            data['success'] = False
                            data['message'] = "item does not exist"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            lecture_ref.delete()
                            data['success'] = True
                            data['message'] = "LECTURE deleted"
                            return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/content/lecture/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            