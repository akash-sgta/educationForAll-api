from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from content_delivery.models import (
        Reply,
        ReplyToReply,
        Post,
    )

# ------------------------------------------------------------

class Votes_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()
    
    def get(self, request, word=None, pk=None, case=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        if(word not in (None, "") or pk not in (None, "") or case not in (None, "") or control not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(not isAuthorizedUSER[0]):
                data['success'] = False
                data['message'] = f"USER_NOT_AUTHORIZED"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if(word.lower() == "post"):
                    try:
                        ref = Post.objects.get(post_id = pk)
                        type = "Post"
                    except Post.DoesNotExist:
                        data['success'] = False
                        data['message'] = "INVALID_POST_ID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                elif(word.lower() == "reply"):
                    try:
                        ref = Reply.objects.get(reply_id = pk)
                        type = "Reply"
                    except Reply.DoesNotExist:
                        data['success'] = False
                        data['message'] = "INVALID_REPLY_ID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    try:
                        ref = ReplyToReply.objects.get(reply_id = pk)
                        type = "Reply2"
                    except ReplyToReply.DoesNotExist:
                        data['success'] = False
                        data['message'] = "INVALID_REPLY2_ID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                
                if(case.lower() == 'u'):
                    type2 = "upvote"
                    ref.upvote += 1
                else:
                    type2 = "downvote"
                    ref.downvote += 1
                ref.save()
                data['success'] = True
                data['message'] = f"{type.upper()}_{type2.upper()}_INCREMENTED"
                return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/content/votes/<post or reply or replyD>/<id>/<u or d>'
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

        data["Allow"] = "GET OPTIONS".split()
        
        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()
        
        data["name"] = "Vote"
        
        temp["POST"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
