from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from auth_prime.models import (
    User,
)
from auth_prime.serializer import (
    User_Serializer,
)

from content_delivery.models import (
    Coordinator,
    Subject,
    Subject_Coordinator,
    Post,
    Assignment,
    Lecture,
    Forum,
    Reply,
    ReplyToReply,
    Video,
)
from content_delivery.serializer import Subject_Serializer, Post_Serializer

from user_personal.models import (
    Notification,
    Enroll,
    User_Notification,
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
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        isAuthorizedUSER = am_I_Authorized(request, "USER")
        if isAuthorizedUSER[0] == False:
            data["success"] = False
            data["message"] = f"USER_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                post_de_serialized = Post_Serializer(data=request.data)
                Subject_Coordinator.objects.get(
                    coordinator_ref=Coordinator.objects.get(user_ref=isAuthorizedUSER[1]),
                    subject_ref=post_de_serialized.initial_data["subject_ref"],
                )
            except Coordinator.DoesNotExist:
                data["success"] = False
                data["message"] = "USER_NOT_COORDINATOR"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            except Subject_Coordinator.DoesNotExist:  # TODO : Only accessed subject post can be created by coordinators
                data["success"] = False
                data["message"] = "COORDINATOR_NOT_ACCESSED_TO_SUBJECT"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            except KeyError or ValueError:
                data["success"] = False
                data["message"] = "CHECK_SUBJECT_ID_KEY"
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                post_de_serialized.initial_data["user_ref"] = isAuthorizedUSER[1]
                if post_de_serialized.is_valid():
                    post_de_serialized.save()

                    # FIX : Check if this section can be put in a seperate thread ?
                    # TODO : create notification for concerned part(y/ies)
                    message = f"Date : {post_de_serialized.data['made_date'].split('T')[0]}"
                    try:
                        message += f"\n\n<b>{Subject.objects.get(pk = post_de_serialized.data['subject_ref']).name}</b>"
                    except Subject.DoesNotExist:
                        message += f"\n\n<b>Ambiguous</b>"
                    message += f"\n\n<i>{post_de_serialized.data['name']}</i>"
                    message += f"\n{' '.join(post_de_serialized.data['body'].split()[:10])}...<a href='#'>[Read More]</a>"
                    try:
                        user_ref = User.objects.get(user_ref=post_de_serialized.data["user_ref"])
                    except User.DoesNotExist:
                        message += f"\n\nCreated By : Anonymous"
                    else:
                        if user_ref.profile_ref == None:
                            message += f"\n\nCreated By : {user_ref.first_name} {user_ref.last_name}"
                        else:
                            message += f"""\n\nCreated By : <a href="#">{user_ref.first_name} {user_ref.last_name}</a>"""
                    notification_ref_new = Notification(
                        post_ref=Post.objects.get(pk=post_de_serialized.data["pk"]), body=message
                    )
                    notification_ref_new.save()
                    # ---------------------------------------------------
                    users = [
                        one["user_ref"]
                        for one in Enroll.objects.filter(subject_ref=post_de_serialized.data["subject_ref"]).values("user_ref")
                    ]
                    coordinators = [
                        one["coordinator_ref"]
                        for one in Subject_Coordinator.objects.filter(
                            subject_ref=post_de_serialized.data["subject_ref"]
                        ).values("coordinator_ref")
                    ]
                    for one in users:
                        User_Notification(notification_ref=notification_ref_new, user_ref=User.objects.get(pk=one)).save()
                    for one in coordinators:
                        User_Notification(
                            notification_ref=notification_ref_new, user_ref=Coordinator.objects.get(pk=one).user_ref
                        ).save()
                    # TODO : =================================================================

                    data["success"] = True
                    data["data"] = post_de_serialized.data
                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    data["success"] = False
                    data["message"] = post_de_serialized.errors
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if int(pk) == 87795962440396049328460600526719:  # TODO : ADMIN asking for all posts
                    isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                    if isAuthorizedADMIN > 0:
                        data["success"] = True
                        data["data"] = Post_Serializer(Post.objects.all().order_by("-id"), many=True).data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data["success"] = False
                        data["message"] = "USER_NOT_ADMIN"
                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                elif int(pk) == 13416989436929794359012690353783:  # TODO : Coordintor asks for respective subject posts
                    try:
                        coordinator_id = Coordinator.objects.get(user_ref=isAuthorizedUSER[1]).pk
                    except Coordinator.DoesNotExist:
                        data["success"] = False
                        data["message"] = "USER_NOT_COORDINATOR"
                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        subjects = [
                            one["subject_ref"]
                            for one in Subject_Coordinator.objects.filter(coordinator_ref=coordinator_id).values("subject_ref")
                        ]
                        temp = list()
                        for sub_id in subjects:
                            temp.extend(
                                Post_Serializer(Post.objects.filter(subject_ref=sub_id).order_by("-id"), many=True).data
                            )
                        data["success"] = True
                        data["data"] = temp.copy()
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                elif int(pk) == 0:  # TODO : User asking for all posts under enrolled subjects
                    subjects = [
                        one["subject_ref"] for one in Enroll.objects.filter(user_ref=isAuthorizedUSER[1]).values("subject_ref")
                    ]
                    temp = list()
                    for sub_id in subjects:
                        temp.extend(Post_Serializer(Post.objects.filter(subject_ref=sub_id).order_by("-id"), many=True).data)
                    data["success"] = True
                    data["data"] = temp.copy()
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:  # TODO : User asking for specific post
                    try:
                        post_ref = Post.objects.get(pk=int(pk))
                    except Post.DoesNotExist:
                        data["success"] = False
                        data["message"] = "POST_ID_INVALID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        post_ref.views += 1
                        post_ref.save()
                        data["success"] = True
                        data["data"] = Post_Serializer(post_ref, many=False).data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/content/post/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    post_de_serialized = Post_Serializer(data=request.data)
                    Subject_Coordinator.objects.get(
                        coordinator_ref=Coordinator.objects.get(user_ref=isAuthorizedUSER[1]),
                        subject_ref=post_de_serialized.initial_data["subject_ref"],
                    )
                except Coordinator.DoesNotExist:
                    data["success"] = False
                    data["message"] = "USER_NOT_COORDINATOR"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                except Subject_Coordinator.DoesNotExist:  # TODO : Only accessed subject post can be edited by coordinators
                    data["success"] = False
                    data["message"] = "COORDINATOR_NOT_ACCESSED_TO_SUBJECT"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                except KeyError:
                    data["success"] = False
                    data["message"] = "CHECK_SUBJECT_ID_KEY"
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    try:
                        post_ref = Post.objects.get(pk=int(pk), user_ref=isAuthorizedUSER[1])
                    except Post.DoesNotExist:
                        data["success"] = False
                        data["message"] = "POST_DOES_NOT_BELONG_TO_USER"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        post_de_serialized = Post_Serializer(post_ref, data=request.data)
                        if post_de_serialized.is_valid():
                            post_de_serialized.save()
                            data["success"] = True
                            data["data"] = post_de_serialized.data
                            return Response(data=data, status=status.HTTP_201_CREATED)
                        else:
                            data["success"] = False
                            data["message"] = post_de_serialized.errors
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/content/post/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    coordinator_ref = Coordinator.objects.get(user_ref=isAuthorizedUSER[1])
                except Coordinator.DoesNotExist:
                    data["success"] = False
                    data["message"] = "USER_NOT_COORDINATOR"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if int(pk) == 87795962440396049328460600526719:  # TODO : Admin deletes all posts
                        Video.objects.all().delete()
                        Forum.objects.all().delete()
                        Lecture.objects.all().delete()
                        Assignment.objects.all.delete()
                        Post.objects.all().delete()
                        data["success"] = True
                        data["message"] = "ADMIN : ALL_POSTS_DELETED"
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:
                        try:
                            post_ref = None
                            post_ref = Post.objects.get(pk=int(pk))
                        except Post.DoesNotExist:
                            data["success"] = False
                            data["message"] = "INVALID_POST_ID"
                            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            flag = (False, "")
                            if post_ref.user_ref.pk != isAuthorizedUSER[1]:
                                if am_I_Authorized(request, "ADMIN") < 1:
                                    data["success"] = False
                                    data["message"] = "USER_NOT_ADMIN"
                                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                                else:  # TODO : Admin : delete specific post
                                    flag = (True, "ADMIN : ")
                            else:  # TODO : Self Post delete
                                flag = (True, "")

                            if flag[0]:
                                if post_ref.video_ref != None:
                                    post_ref.video_ref.delete()
                                if post_ref.lecture_ref != None:
                                    post_ref.lecture_ref.delete()
                                if post_ref.forum_ref != None:
                                    post_ref.forum_ref.delete()
                                if post_ref.assignment_ref != None:
                                    post_ref.assignment_ref.delete()
                                post_ref.delete()
                                data["success"] = True
                                data["message"] = flag[1] + "POST_DELETED"
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/content/post/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        temp = dict()

        data["Allow"] = "POST GET PUT DELETE OPTIONS".split()

        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()

        data["name"] = "Post"

        temp["POST"] = {
            "video_ref": "Number [FK] / null",
            "forum_ref": "Number [FK] / null",
            "assignment_ref": "Number [FK] / null",
            "lecture_ref": "Number [FK] / null",
            "subject_ref": "Number [FK] / null",
            "name": "String : 128",
            "body": "String : unl",
        }
        temp["GET"] = None
        temp["PUT"] = {
            "video_ref": "Number [FK] / null",
            "forum_ref": "Number [FK] / null",
            "assignment_ref": "Number [FK] / null",
            "lecture_ref": "Number [FK] / null",
            "subject_ref": "Number [FK] / null",
            "name": "String : 128",
            "body": "String : unl",
        }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
