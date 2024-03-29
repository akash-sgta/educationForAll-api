from auth_prime.important_modules import am_I_Authorized, random_generator
from content_delivery.models import Assignment, Coordinator, Post, Subject_Coordinator
from content_delivery.serializer import Assignment_Serializer
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from user_personal.models import Enroll, Submission
import re
import threading

from analytics.models import Permalink

# ------------------------------------------------------------


class UnCheck_Submission(threading.Thread):
    def __init__(self, name):
        super().__init__(name=f"UNCHECK_{name}")
        self.pk = int(name)

    def run(self):
        for sub in Submission.objects.filter(assignment_ref=self.pk):
            sub.checked = False
            sub.save()


class Clear_Permalink(threading.Thread):
    def __init__(self, name):
        super().__init__(name=f"PERML_{name}")
        self.pk = int(name)

    def run(self):
        Permalink.objects.filter(ref__exact={"class": str(Assignment), "pk": self.pk}).delete()


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
        profile = Assignment_Serializer(
            Assignment.objects.get(pk=self.pk), data=Assignment_Serializer(Assignment.objects.get(pk=self.pk), many=False).data
        )

        if profile.initial_data["external_url_1"] not in (None, ""):
            if not self.check(profile.initial_data["external_url_1"]):
                permalink_ref = Permalink(
                    ref={"class": str(Assignment), "pk": profile.initial_data["id"]},
                    name=random_generator(16),
                    body=profile.initial_data["external_url_1"],
                )
                permalink_ref.save()
                profile.initial_data["external_url_1"] = f"/api/analytics/perm/{permalink_ref.name}"

        if profile.initial_data["external_url_2"] not in (None, ""):
            if not self.check(profile.initial_data["external_url_2"]):
                permalink_ref = Permalink(
                    ref={"class": str(Assignment), "pk": profile.initial_data["id"]},
                    name=random_generator(16),
                    body=profile.initial_data["external_url_2"],
                )
                permalink_ref.save()
                profile.initial_data["external_url_2"] = f"/api/analytics/perm/{permalink_ref.name}"

        if profile.is_valid():
            profile.save()
        else:
            print(profile.errors)


class Assignment_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None):  # TODO : Only Coordinator can create assignment
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
                coordinator_ref = Coordinator.objects.get(user_ref=isAuthorizedUSER[1])
            except Coordinator.DoesNotExist:
                data["success"] = False
                data["message"] = "USER_NOT_COORDINATOR"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                assignment_de_serialized = Assignment_Serializer(data=request.data)
                if assignment_de_serialized.is_valid():
                    assignment_de_serialized.save()

                    Set_Permalink(assignment_de_serialized.data["id"]).start()

                    data["success"] = True
                    data["data"] = assignment_de_serialized.data
                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    data["success"] = False
                    data["message"] = assignment_de_serialized.errors
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
                if (
                    int(pk) == 87795962440396049328460600526719
                ):  # TODO : User can see all assignments respect to enrolled subjects
                    enroll = Enroll.objects.filter(user_ref=isAuthorizedUSER[1]).values("subject_ref")
                    data["success"] = True
                    data["data"] = list()
                    for post in Post.objects.filter(subject_ref__in=[int(sub["subject_ref"]) for sub in enroll]):
                        if post.assignment_ref != None:
                            assignment_ref = post.assignment_ref
                            data["data"].append(
                                {
                                    "assignment": Assignment_Serializer(assignment_ref, many=False).data,
                                    "submission": [
                                        one["pk"]
                                        for one in Submission.objects.filter(assignment_ref=assignment_ref)
                                        .order_by("-pk")
                                        .values("pk")
                                    ],
                                }
                            )
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
                elif int(pk) == 0:  # TODO : Coordinator looks for assignments under them
                    try:
                        coordinator_id = Coordinator.objects.get(user_ref=isAuthorizedUSER[1]).pk
                    except Coordinator.DoesNotExist:
                        data["success"] = False
                        data["message"] = "USER_NOT_COORDINATOR"
                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        post_ref = Post.objects.filter(
                            subject_ref__in=[
                                int(sub["subject_ref"])
                                for sub in Subject_Coordinator.objects.filter(coordinator_ref=coordinator_id).values(
                                    "subject_ref"
                                )
                            ]
                        )
                        data["success"] = True
                        data["data"] = list()
                        for post in post_ref:
                            if post.assignment_ref != None:
                                assignment_ref = post.assignment_ref
                                data["data"].append(
                                    {
                                        "assignment": Assignment_Serializer(assignment_ref, many=False).data,
                                        "submission": [
                                            one["pk"]
                                            for one in Submission.objects.filter(assignment_ref=assignment_ref).values("pk")
                                        ],
                                    }
                                )
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:  # TODO : Any user looking for assignment
                    try:
                        assignment_ref = Assignment.objects.get(pk=int(pk))
                    except Assignment.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_ASSIGNMENT_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data["success"] = True
                        try:
                            submission_pk = [
                                Submission.objects.get(assignment_ref=assignment_ref, user_ref=isAuthorizedUSER[1]).pk
                            ]
                        except Submission.DoesNotExist:
                            submission_pk = []
                        except Submission.MultipleObjectsReturned:
                            submission_pk = [
                                one["pk"]
                                for one in Submission.objects.filter(
                                    assignment_ref=assignment_ref, user_ref=isAuthorizedUSER[1]
                                )
                                .order_by("-pk")
                                .values("pk")
                            ]
                        data["data"] = {
                            "assignment": Assignment_Serializer(assignment_ref, many=False).data,
                            "submission": submission_pk,
                        }
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/content/assignment/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):  # TODO : Only Coordinator can edit assignment
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
                    try:
                        assignment_ref = Assignment.objects.get(pk=int(pk))
                    except Assignment.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_ASSIGNMENT_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        assignment_de_serialized = Assignment_Serializer(assignment_ref, data=request.data)
                        if assignment_de_serialized.is_valid():
                            assignment_de_serialized.save()

                            Clear_Permalink(assignment_de_serialized.data["id"]).start()
                            Set_Permalink(assignment_de_serialized.data["id"]).start()

                            UnCheck_Submission(assignment_de_serialized.data["id"]).start()

                            data["success"] = True
                            data["data"] = assignment_de_serialized.data
                            return Response(data=data, status=status.HTTP_201_CREATED)
                        else:
                            data["success"] = False
                            data["message"] = assignment_de_serialized.errors
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/content/assignment/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):  # TODO : Only Coordinator can delete assignment
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
                    coordinator_ref = Coordinator.objects.filter(user_ref=isAuthorizedUSER[1])
                except Coordinator.DoesNotExist:
                    data["success"] = False
                    data["message"] = "USER_NOT_COORDINATOR"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        assignment_ref = Assignment.objects.get(pk=int(pk))
                    except Assignment.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_ASSIGNMENT_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        Clear_Permalink(assignment_ref.pk).start()

                        assignment_ref.delete()
                        data["success"] = True
                        data["message"] = "ASSIGNMENT_DELETED"
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/content/assignment/<id>"}
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

        data["name"] = "Assignment"

        temp["POST"] = {
            "body": "String : unl",
            "external_url_1": "String : 255 / null",
            "external_url_2": "String : 255 / null",
            "total_marks": "Number",
        }
        temp["GET"] = None
        temp["PUT"] = {
            "body": "String : unl",
            "external_url_1": "String : 255 / null",
            "external_url_2": "String : 255 / null",
            "total_marks": "Number",
        }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
