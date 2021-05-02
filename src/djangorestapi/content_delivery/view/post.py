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
        Post
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
                post_de_serialized = Post_Serializer(data = request.data)
                post_de_serialized.initial_data['user_credential_id'] = isAuthorizedUSER[1]
                if(post_de_serialized.is_valid()):
                    post_de_serialized.save()
                    # create notification for concerned part(y/ies)
                    # ---------------------------------------------
                    message = f"Date : {post_de_serialized.data['made_date'].split('T')[0]}"
                    message += f'''
                    \n\n<b>{Subject_Serializer(Subject.objects.get(subject_id = post_de_serialized.data['subject_id']), many=False).data['subject_name']}</b>
                    \n\n<i>{post_de_serialized.data['post_name']}</i>
                    \n{' '.join(post_de_serialized.data['post_body'].split()[:10])}...<a href="http://{host}/api/content/post/read/{post_de_serialized.data['post_id']}">[Read More]</a>
                    '''
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
                    # ---------------------------------------------
                    data['success'] = True
                    data['data'] = post_de_serialized.data
                    return Response(data = data, status=status.HTTP_201_CREATED)
                else:
                    data['success'] = False
                    data['message'] = post_de_serialized.errors
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
                    enroll_ref_list = Enroll.objects.filter(user_credential_id = isAuthorizedUSER[1]).values('subject_id')
                    temp = list()
                    for sub_id in enroll_ref_list:
                        temp.extend(Post_Serializer(Post.objects.all().order_by('-pk'), many=True).data)
                    data['success'] = True
                    data['data'] = temp.copy()
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                else:
                    try:
                        post_ref = Post.objects.get(post_id = int(pk))
                    except Post.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
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
                        post_ref = Post.objects.get(post_id = int(pk), user_credential_id = isAuthorizedUSER[1])
                    except Post.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist or does not belong to user"
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
                        Post.objects.all().delete()
                        data['success'] = True
                        data['message'] = "All POST(s) deleted"
                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            post_ref = Post.objects.get(post_id = int(pk), user_credential_id = isAuthorizedUSER[1])
                        except Post.DoesNotExist:
                            data['success'] = False
                            data['message'] = "item does not exist or does not belong to user"
                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            post_ref.delete()
                            data['success'] = True
                            data['message'] = "POST deleted"
                            return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/content/post/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
            