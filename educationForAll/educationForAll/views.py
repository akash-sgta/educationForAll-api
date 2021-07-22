from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

@api_view(['GET'])
def check_server_status(request):
    date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    message = f'Server is live with current time : {date}'
    return Response(data=message, status=status.HTTP_200_OK)