import threading

from auth_prime.important_modules import am_I_Authorized
from content_delivery.models import AssignmentMCQ, Coordinator, Post, Subject_Coordinator
from content_delivery.serializer import AssignmentMCQ_Serializer
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from user_personal.models import Enroll, SubmissionMCQ

# ------------------------------------------------------------


class Auto_Mark_MCQ(threading.Thread):
    def __init__(self, name):
        super().__init__(name=f"AMMC_{name}")
        self.submission_ref = SubmissionMCQ.objects.get(pk=int(name))
        self.assignment_ref = self.submission_ref.assignment_ref
        self.assignment = self.assignment_ref.body
        self.submission = self.submission_ref.body
        if self.submission_ref.checked == True:
            del self

    def run(self):
        total, count, scored = self.assignment_ref.total_score, 0, 0
        for ans in self.submission.items():
            if ans[1] == self.assignment[ans[0]]["ans"]:
                scored += 1
            count += 1
        if count == total:
            self.submission_ref.marks = scored
        else:
            self.assignment_ref.total_score = 100
            self.submission_ref.marks = round((scored / count) * 100, 2)
            self.assignment_ref.save()
        self.submission_ref.checked = True
        self.submission_ref.save()


class ReCheck_Submission(threading.Thread):
    def __init__(self, name):
        super().__init__(name=f"RECHECK_{name}")
        self.pk = int(name)

    def run(self):
        for sub in SubmissionMCQ.objects.filter(assignment_ref=self.pk).values("pk"):
            Auto_Mark_MCQ(sub["pk"]).start()


# ------------------------------------------------------------
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
                assignment_de_serialized = AssignmentMCQ_Serializer(data=request.data)
                if assignment_de_serialized.is_valid():
                    assignment_de_serialized.save()
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
                    for post in Post.object.filter(subject_ref__in=[int(sub["subject_ref"]) for sub in enroll]):
                        if post.assignment_ref != None:
                            assignment_ref = post.assignment_ref
                            data["data"].append(
                                {
                                    "assignment": AssignmentMCQ_Serializer(assignment_ref, many=False).data,
                                    "submission": [
                                        one["pk"]
                                        for one in SubmissionMCQ.objects.filter(assignment_ref=assignment_ref)
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
                        post_ref = Post.object.filter(
                            subject_ref__in=[
                                int(sub["subject_ref"])
                                for sub in Subject_Coordinator.objects.filter(coordinator_id=coordinator_id).values(
                                    "subject_ref"
                                )
                            ]
                        )
                        data["success"] = True
                        data["data"] = list()
                        for post in post_ref:
                            if post.assignmentMCQ_ref != None:
                                assignment_ref = post.assignmentMCQ_ref
                                data["data"].append(
                                    {
                                        "assignment": AssignmentMCQ_Serializer(assignment_ref, many=False).data,
                                        "submission": [
                                            one["pk"]
                                            for one in SubmissionMCQ.objects.filter(assignment_ref=assignment_ref)
                                            .order_by("-pk")
                                            .values("pk")
                                        ],
                                    }
                                )
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:  # TODO : Any user looking for assignment
                    try:
                        assignment_ref = AssignmentMCQ.objects.get(pk=int(pk))
                    except AssignmentMCQ.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_ASSIGNMENT_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data["success"] = True
                        try:
                            submission_pk = [
                                SubmissionMCQ.objects.get(assignment_ref=assignment_ref, user_ref=isAuthorizedUSER[1]).pk
                            ]
                        except SubmissionMCQ.DoesNotExist:
                            submission_pk = []
                        except SubmissionMCQ.MultipleObjectsReturned:
                            submission_pk = [
                                one["pk"]
                                for one in SubmissionMCQ.objects.filter(
                                    assignment_ref=assignment_ref, user_ref=isAuthorizedUSER[1]
                                )
                                .order_by("-pk")
                                .values("pk")
                            ]
                        data["data"] = {
                            "assignment": AssignmentMCQ_Serializer(assignment_ref, many=False).data,
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
                        assignment_ref = AssignmentMCQ.objects.get(pk=int(pk))
                    except AssignmentMCQ.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_ASSIGNMENT_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        assignment_de_serialized = AssignmentMCQ_Serializer(assignment_ref, data=request.data)
                        if assignment_de_serialized.is_valid():
                            assignment_de_serialized.save()

                            ReCheck_Submission(assignment_de_serialized.data["id"]).start()

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
                        assignment_ref = AssignmentMCQ.objects.get(assignment_ref=int(pk))
                    except AssignmentMCQ.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_ASSIGNMENT_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
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
            "body": "JSON DATA",
            "total_marks": "Number",
        }
        temp["GET"] = None
        temp["PUT"] = {
            "body": "JSON DATA",
            "total_marks": "Number",
        }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
