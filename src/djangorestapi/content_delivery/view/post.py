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
    )
from auth_prime.serializer import (
        User_Credential_Serializer,
    )

from content_delivery.models import (
        Coordinator,
        Subject,
        Subject_Coordinator_Int,
        Post,
        Assignment,
        Lecture,
        Forum,
        Reply,
        ReplyToReply,
        Video
    )
from content_delivery.serializer import (
        Subject_Serializer,
        Post_Serializer
    )
    
from user_personal.models import (
    Notification,
    Enroll,
    User_Notification_Int,
)

# ------------------------------------------------------------

host = ""

class Post_View(APIView):

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
            try:
                post_de_serialized = Post_Serializer(data = request.data)
                Subject_Coordinator_Int.objects.get(
                    coordinator_id = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1]).coordinator_id,
                    subject_id = post_de_serialized.initial_data['subject_id'])
            except Coordinator.DoesNotExist:
                data['success'] = False
                data['message'] = "USER_NOT_COORDINATOR"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            except Subject_Coordinator_Int.DoesNotExist: # TODO : Only accessed subject post can be created by coordinators
                data['success'] = False
                data['message'] = "COORDINATOR_NOT_ACCESSED_TO_SUBJECT"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            except KeyError:
                data['success'] = False
                data['message'] = "CHECK_SUBJECT_ID_KEY"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            else:
                post_de_serialized.initial_data['user_credential_id'] = isAuthorizedUSER[1]
                if(post_de_serialized.is_valid()):
                    post_de_serialized.save()

                    # TODO : create notification for concerned part(y/ies)
                    message = f"Date : {post_de_serialized.data['made_date'].split('T')[0]}"
                    try:
                        message += f"\n\n<b>{Subject_Serializer(Subject.objects.get(subject_id = post_de_serialized.data['subject_id']), many=False).data['subject_name']}</b>"
                    except Subject.DoesNotExist:
                        message += f"\n\n<b>Ambiguous</b>"
                    message += f"\n\n<i>{post_de_serialized.data['post_name']}</i>"
                    message += f"\n{' '.join(post_de_serialized.data['post_body'].split()[:10])}...<a href='http://{host}/api/content/post/read/{post_de_serialized.data['post_id']}'>[Read More]</a>"
                    try:
                        serialized = User_Credential_Serializer(User_Credential.objects.get(user_credential_id = post_de_serialized.data['user_credential_id']), many=False).data
                    except Exception as ex:
                        print("EX : ", ex)
                        message += f"\n\nCreated By : Anonymous"
                    else:
                        if(serialized['user_profile_id'] in (None, "")):
                            message += f"\n\nCreated By : {serialized['user_f_name']} {serialized['user_l_name']}"
                        else:
                            message += f'''\n\nCreated By : <a href="http://{host}/api/user/prof/read/{serialized['user_profile_id']}">{serialized['user_f_name']} {serialized['user_l_name']}</a>'''
                    notification_ref_new = Notification(
                                                post_id = Post.objects.get(post_id = post_de_serialized.data['post_id']),
                                                notification_body = message
                                            )
                    notification_ref_new.save()
                    many_to_many_enroll = Enroll.objects.filter(subject_id = post_de_serialized.data['subject_id'])
                    many_to_many_coor_sub = Subject_Coordinator_Int.objects.filter(subject_id = post_de_serialized.data['subject_id'])
                    if(len(many_to_many_coor_sub) > 0):
                        for one in many_to_many_coor_sub:
                            User_Notification_Int(
                                notification_id = notification_ref_new,
                                user_credential_id = one.coordinator_id.user_credential_id
                            ).save()
                    if(len(many_to_many_enroll) > 0):
                        for one in many_to_many_enroll:
                            User_Notification_Int(
                                notification_id = notification_ref_new,
                                user_credential_id = one.user_credential_id
                            ).save()
                    # TODO : =================================================================
                    data['success'] = True
                    data['data'] = post_de_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = post_de_serialized.errors
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
                if(int(pk) == 87795962440396049328460600526719): # TODO : ADMIN asking for all posts
                    isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                    if(isAuthorizedADMIN > 0):
                        data['success'] = True
                        data['data'] = Post_Serializer(Post.objects.all().order_by("-post_id"), many=True).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data['success'] = False
                        data['message'] = "USER_NOT_ADMIN"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                elif(int(pk) == 13416989436929794359012690353783): # TODO : Coordintor asks for respective subject posts
                    try:
                        coordinator_id = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1]).coordinator_id
                    except Coordinator.DoesNotExist:
                        data['success'] = False
                        data['message'] = "USER_NOT_COORDINATOR"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        sub_coor_ref_ids = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_id).values('subject_id')
                        temp = list()
                        for sub_id in sub_coor_ref_ids:
                            temp.extend(Post_Serializer(Post.objects.filter(subject_id = sub_id['subject_id']).order_by("-post_id"), many=True).data)
                        data['success'] = True
                        data['data'] = temp.copy()
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                elif(int(pk) == 0): # TODO : User asking for all posts under enrolled subjects
                    try:
                        enroll_sub_ids = Enroll.objects.filter(user_credential_id = isAuthorizedUSER[1]).values('subject_id')
                    except Enroll.DoesNotExist:
                        data['success'] = False
                        data['message'] = "USER_NOT_ENROLLED"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        temp = list()
                        for sub_id in enroll_sub_ids:
                            temp.extend(Post_Serializer(Post.objects.filter(subject_id = sub_id['subject_id']).order_by("-post_id"), many=True).data)
                        data['success'] = True
                        data['data'] = temp.copy()
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else: # TODO : User asking for specific post
                    try:
                        post_ref = Post.objects.get(post_id = int(pk))
                    except Post.DoesNotExist:
                        data['success'] = False
                        data['message'] = "POST_ID_INVALID"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        post_ref.post_views += 1
                        post_ref.save()
                        data['success'] = True
                        data['data'] = Post_Serializer(post_ref, many=False).data
                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/content/post/<id>'
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
                    post_de_serialized = Post_Serializer(data = request.data)
                    Subject_Coordinator_Int.objects.get(
                        coordinator_id = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1]).coordinator_id,
                        subject_id = post_de_serialized.initial_data['subject_id'])
                except Coordinator.DoesNotExist:
                    data['success'] = False
                    data['message'] = "USER_NOT_COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                except Subject_Coordinator_Int.DoesNotExist: # TODO : Only accessed subject post can be edited by coordinators
                    data['success'] = False
                    data['message'] = "COORDINATOR_NOT_ACCESSED_TO_SUBJECT"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                except KeyError:
                    data['success'] = False
                    data['message'] = "CHECK_SUBJECT_ID_KEY"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    try:
                        post_ref = Post.objects.get(post_id = int(pk), user_credential_id = isAuthorizedUSER[1])
                    except Post.DoesNotExist:
                        data['success'] = False
                        data['message'] = "POST_DOES_NOT_BELONG_TO_USER"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        post_de_serialized = Post_Serializer(post_ref, data=request.data)
                        if(post_de_serialized.is_valid()):
                            post_de_serialized.save()
                            data['success'] = True
                            data['data'] = post_de_serialized.data
                            return Response(data = data, status=status.HTTP_201_CREATED)
                        else:
                            data['success'] = False
                            data['message'] = post_de_serialized.errors
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/content/post/<id>'
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
                    coordinator_ref = Coordinator.objects.get(user_credential_id = isAuthorizedUSER[1])
                except Coordinator.DoesNotExist:
                    data['success'] = False
                    data['message'] = "USER_NOT_COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if(int(pk) == 87795962440396049328460600526719): # TODO : Admin deletes all posts
                        Video.objects.all().delete()
                        Forum.objects.all().delete()
                        Lecture.objects.all().delete()
                        Assignment.objects.all.delete()
                        Post.objects.all().delete()
                        data['success'] = True
                        data['message'] = "ADMIN : ALL_POSTS_DELETED"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            post_ref = None
                            post_ref = Post.objects.get(post_id = int(pk))
                        except Post.DoesNotExist:
                            if(post_ref == None):
                                data['success'] = False
                                data['message'] = "INVALID_POST_ID"
                                return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            if(post_ref.user_credential_id.user_credential_id != isAuthorizedUSER[1] and am_I_Authorized(request, "ADMIN") < 1):
                                data['success'] = False
                                data['message'] = "USER_NOT_ADMIN"
                                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                if(post_ref.video_id != None):
                                    post_ref.video_id.delete()
                                if(post_ref.lecture_id != None):
                                    post_ref.lecture_id.delete()
                                if(post_ref.forum_id != None):
                                    post_ref.forum_id.delete()
                                if(post_ref.assignment_id != None):
                                    post_ref.assignment_id.delete()
                                post_ref.delete()
                                data['success'] = True
                                data['message'] = "POST_DELETED"
                                return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/content/post/<id>'
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
        
        data["name"] = "Post"
        
        temp["POST"] = {
                "video_id" : "Number/null",

                "forum_id" : "Number/null",
                "assignment_id" : "Number/null",
                "lecture_id" : "Number/null",
                "subject_id" : "Number/null",
                            
                "post_name" : "String",
                "post_body" : "String"
            }
        temp["GET"] = None
        temp["PUT"] = {
                "video_id" : "Number/null",

                "forum_id" : "Number/null",
                "assignment_id" : "Number/null",
                "lecture_id" : "Number/null",
                "subject_id" : "Number/null",
                            
                "post_name" : "String",
                "post_body" : "String"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
