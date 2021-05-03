from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from datetime import datetime, timedelta
# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from analytics.models import (
        Log
    )
from analytics.serializer import (
        Log_Serializer
    )

# ------------------------------------------------------------

class Log_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def get(self, request, date=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        if(date not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                isAuthorizedAPI = am_I_Authorized(request, "API")
                if(not isAuthorizedAPI):
                    data['success'] = False
                    data['message'] = f"error:API_NOT_AUTHORIZED, message:{isAuthorizedAPI[1]}"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    data['success'] = True
                    date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d').split()[0]
                    data['date'] = Log_Serializer(Log.objects.filter(made_date__startswith=date, api_token_id=isAuthorizedAPI[1]).order_by('-log_id'), many=True).data
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/analytics/log/<dd-mm-yyyy>'
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

        data["Allow"] = "GETOPTIONS".split()
        
        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()
        
        data["name"] = "Log"
        
        temp["GET"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)

