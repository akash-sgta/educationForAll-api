import re
import threading

from analytics.models import Permalink
from auth_prime.important_modules import am_I_Authorized, random_generator
from content_delivery.models import Assignment, Coordinator, Post, Subject_Coordinator
from content_delivery.serializer import Assignment_Serializer
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from user_personal.models import Submission
from user_personal.serializer import Submission_Serializer

# ------------------------------------------------------------


class Clear_Permalink(threading.Thread):
    def __init__(self, name):
        super().__init__(name=f"PERML_{name}")
        self.pk = int(name)

    def run(self):
        Permalink.objects.filter(ref__exact={"class": str(Submission), "pk": self.pk}).delete()


class Set_Permalink(threading.Thread):
    def __init__(self, name):
        super().__init__(name=f"PERML_{name}")
        self.pk = int(name)

    def check(self, data):
        if re.search("api/analytics/perm", data) != None:
            return True
        else:
            return False

    def run(self):
        profile = Submission_Serializer(
            Submission.objects.get(pk=self.pk), data=Submission_Serializer(Submission.objects.get(pk=self.pk), many=False).data
        )

        if profile.initial_data["external_url_1"] not in (None, ""):
            if not self.check(profile.initial_data["external_url_1"]):
                permalink_ref = Permalink(
                    ref={"class": str(Submission), "pk": profile.initial_data["id"]},
                    name=random_generator(16),
                    body=profile.initial_data["external_url_1"],
                )
                permalink_ref.save()
                profile.initial_data["external_url_1"] = f"/api/analytics/perm/{permalink_ref.name}"

        if profile.initial_data["external_url_2"] not in (None, ""):
            if not self.check(profile.initial_data["external_url_2"]):
                permalink_ref = Permalink(
                    ref={"class": str(Submission), "pk": profile.initial_data["id"]},
                    name=random_generator(16),
                    body=profile.initial_data["external_url_2"],
                )
                permalink_ref.save()
                profile.initial_data["external_url_2"] = f"/api/analytics/perm/{permalink_ref.name}"

        if profile.is_valid():
            profile.save()
        else:
            print(profile.errors)


class Submission_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None, pkk=None):
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
            submission_de_serialized = Submission_Serializer(data=request.data)
            submission_de_serialized.initial_data["user_ref"] = int(isAuthorizedUSER[1])
            if submission_de_serialized.is_valid():
                submission_de_serialized.save()

                Set_Permalink(submission_de_serialized.data["id"]).start()

                data["success"] = True
                data["data"] = submission_de_serialized.data
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data["success"] = False
                data["message"] = f"SERIALIZING_ERROR : {submission_de_serialized.errors}"
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, pkk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if not isAuthorizedUSER[0]:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    # /pk_1/pk_2
                    # pk_1 - 0,                                 pk_2 - 0    ->  User demanding all their submission
                    # pk_1 - 0,                                 pk_2 - x    ->  User demanding for submission [x]
                    # pk_1 - 87795962440396049328460600526719,  pk_2 - 0    ->  Coordiantor demanding all submission under all assignments
                    # pk_1 - 87795962440396049328460600526719,  pk_2 - x    ->  Coordiantor demanding all submission under assignment [x]
                    # pk_1 - 13416989436929794359012690353783,  pk_2 - x    ->  Coordinator asking for specific submission
                    if int(pk) == 0:  # TODO : User accessing submission
                        if int(pkk) == 0:  # TODO : All submission
                            submission_ref_list = Submission.objects.filter(user_ref=isAuthorizedUSER[1])
                            data["success"] = True
                            data["data"] = [Submission_Serializer(one, many=False).data for one in submission_ref_list]
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:  # TODO : Specific Submission
                            try:
                                submission_ref = Submission.objects.get(user_ref=isAuthorizedUSER[1], pk=int(pkk))
                            except Submission.DoesNotExist:
                                data["success"] = False
                                data["message"] = "INVALID_SUBMISSION_ID"
                                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                data["success"] = True
                                data["data"] = Submission_Serializer(submission_ref, many=False).data
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif int(pk) == 87795962440396049328460600526719:  # TODO : Coordinator accessing submission
                        if int(pkk) == 0:  # TODO : All submission
                            try:
                                coordinator_id = Coordinator.objects.get(user_ref=isAuthorizedUSER[1]).pk
                            except Coordinator.DoesNotExist:
                                data["success"] = False
                                data["message"] = "USER_NOT_COORDINATOR"
                                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                subject_ids = [
                                    int(one["subject_ref"])
                                    for one in Subject_Coordinator.objects.filter(coordinator_ref=coordinator_id).values(
                                        "subject_ref"
                                    )
                                ]
                                assignment_ids = list()
                                for one in Post.objects.filter(subject_ref__in=subject_ids).values("assignment_ref"):
                                    if one["assignment_ref"] != None:
                                        assignment_ids.append(int(one["assignment_ref"]))
                                assignment_ids = list(set(assignment_ids))
                                temp = list()
                                for one in assignment_ids:
                                    temp.append(
                                        {
                                            "assignment": one,
                                            "submission": Submission_Serializer(
                                                Submission.objects.filter(assignment_ref=one), many=True
                                            ).data,
                                        }
                                    )
                                data["success"] = True
                                data["data"] = temp.copy()
                                return Response(data=data, status=status.HTTP_200_OK)
                        else:  # TODO : Specific Assignment All Submissions
                            try:
                                coordinator_id = Coordinator.objects.get(user_ref=isAuthorizedUSER[1]).pk
                            except Coordinator.DoesNotExist:
                                data["success"] = False
                                data["message"] = "USER_NOT_COORDINATOR"
                                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                try:
                                    post_ref = Post.objects.get(assignment_ref=int(pkk))
                                except Post.DoesNotExist:
                                    data["success"] = False
                                    data["message"] = "ASSIGNMENT_NOT_LINKED"
                                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    if coordinator_id not in [
                                        int(one["coordinator_ref"])
                                        for one in Subject_Coordinator.objects.filter(subject_ref=post_ref.subject_ref).values(
                                            "coordinator_ref"
                                        )
                                    ]:
                                        data["success"] = False
                                        data["message"] = "ASSIGNMENT_NOT_UNDER_COORDINATOR"
                                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                                    else:
                                        data["success"] = True
                                        data["data"] = {
                                            "assignment": int(pkk),
                                            "submission": Submission_Serializer(
                                                Submission.objects.filter(assignment_ref=int(pkk)), many=True
                                            ).data,
                                        }
                                        return Response(data=data, status=status.HTTP_200_OK)
                    elif int(pk) == 13416989436929794359012690353783:
                        if pkk == None:
                            data["success"] = False
                            data["message"] = "INVALID_SUBMISSION_ID"
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                        else:  # TODO : JUST A SINGULAR SUBMISSION
                            try:
                                coordinator_id = Coordinator.objects.get(user_ref=isAuthorizedUSER[1]).pk
                            except Coordinator.DoesNotExist:
                                data["success"] = False
                                data["message"] = "USER_NOT_COORDINATOR"
                                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                            else:
                                try:
                                    submission_ref = Submission.objects.get(pk=int(pkk))
                                except Submission.DoesNotExist:
                                    data["success"] = False
                                    data["message"] = "INVALID_SUBMISSION_ID"
                                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    try:
                                        subject_id = Post.objects.get(
                                            assignment_ref=submission_ref.assignment_ref
                                        ).subject_ref.pk
                                    except Post.DoesNotExist:
                                        data["success"] = False
                                        data["message"] = "ASSIGNMENT_NOT_LINKED"
                                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                                    else:
                                        try:
                                            subjects_coordinator_check = Subject_Coordinator.objects.get(
                                                coordinator_ref=coordinator_id, subject_ref=subject_id
                                            )
                                        except Subject_Coordinator.DoesNotExist:
                                            data["success"] = False
                                            data["message"] = "SUBMISSION_NOT_UNDER_COORDINATOR"
                                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                                        else:
                                            data["success"] = True
                                            data["data"] = Submission_Serializer(submission_ref, many=False).data
                                            return Response(data=data, status=status.HTTP_200_OK)
                except Exception as ex:
                    print("SUB_GET EX : ", ex)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/personal/submission/<id>/<idd>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, pkk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if not isAuthorizedUSER[0]:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    submission_ref = Submission.objects.get(user_ref=isAuthorizedUSER[1], pk=pk)
                except Submission.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_SUBMISSION_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    submission_serialized = Submission_Serializer(submission_ref, data=request.data)
                    submission_serialized.initial_data["user_ref"] = isAuthorizedUSER[1]
                    if submission_serialized.is_valid():
                        submission_serialized.save()

                        Clear_Permalink(submission_serialized.data["id"]).start()
                        Set_Permalink(submission_serialized.data["id"]).start()

                        data["success"] = True
                        data["data"] = submission_serialized.data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:
                        data["success"] = False
                        data["message"] = f"SERIALIZING_ERROR : {submission_serialized.errors}"
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/personal/submission/<id>/"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, pkk=None):
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
                    submission_ref = Submission.objects.get(user_ref=isAuthorizedUSER[1], pk=pk)
                except Submission.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_SUBMISSION_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    Clear_Permalink(submission_ref.pk).start()

                    submission_ref.delete()
                    data["success"] = True
                    data["message"] = "SUBMISSION_DELETED"
                    return Response(data=data)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/personal/submission/<id>/"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None, pkk=None):
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

        data["name"] = "Submission"

        temp["POST"] = {
            "assignment_ref": "Number [FK]",
            "body": "String : unl",
            "external_url_1": "String : 255 / null",
            "external_url_2": "String : 255 / null",
        }
        temp["GET"] = None
        temp["PUT"] = {
            "assignment_ref": "Number [FK]",
            "body": "String : unl",
            "external_url_1": "String : 255 / null",
            "external_url_2": "String : 255 / null",
        }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
