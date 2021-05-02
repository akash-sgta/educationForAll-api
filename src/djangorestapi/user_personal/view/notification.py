from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from user_personal.models import (
        Notification,
        User_Notification_Int
    )
from user_personal.serializer import (
        Notification_Serializer
    )

# ------------------------------------------------------------

class Notification_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def get(self, request, pk=None):
        data = dict()
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(int(pk) == 0):
                    many = User_Notification_Int.objects.filter(user_credential_id = isAuthorizedUSER[1]).values('notification_id')
                    notification_list = list()
                    for one in many:
                        notification_list.append(
                            Notification_Serializer(Notification.objects.get(notification_id = int(one['notification_id'])), many=False).data
                        )
                    data['success'] = True
                    data['data'] = notification_list.copy()
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:
                    try:
                        notification_ref = User_Notification_Int.objects.get(user_credential_id = isAuthorizedUSER[1], pk=int(pk))
                    except User_Notification_Int.DoesNotExist:
                        data['success'] = False
                        data['message'] = "invalid item id"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data['success'] = True
                        data['data'] = Notification_Serializer(notification_ref.notification_id, many=False).data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/personal/notification/<id>'
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
                    notification_ref = User_Notification_Int.objects.get(user_credential_id = isAuthorizedUSER[1], pk = int(pk))
                except User_Notification_Int.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist or does not belong to user"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    notification_ref.delete()
                    data['success'] = True
                    data['message'] = "NOTIFICATION deleted"
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/personal/notification/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)