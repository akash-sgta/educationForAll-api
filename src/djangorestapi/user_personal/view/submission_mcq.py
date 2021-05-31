import threading

from auth_prime.important_modules import am_I_Authorized
from content_delivery.models import AssignmentMCQ, Coordinator, Post, Subject_Coordinator
from content_delivery.serializer import AssignmentMCQ_Serializer
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from user_personal.models import SubmissionMCQ
from user_personal.serializer import SubmissionMCQ_Serializer

# ------------------------------------------------------------


class Auto_Mark_MCQ(threading.Thread):
    def __init__(self, name):
        super().__init__(name=f"AMMC_{name}")
        self.submission_ref = SubmissionMCQ.objects.get(pk=int(name))
        self.assignment_ref = self.submission_ref.assignment_ref
        self.assignment = self.assignment_ref.body
        self.submission = self.submission.body

    def run(self):
        total, count, scored = self.assignment_ref.total_score, 0, 0
        for ans in self.submission.items():
            if ans[1] == self.assignment[ans[0]]["ans"]:
                scored += 1
            count += 1
        if count == total:
            self.submission_ref.marks = scored
            self.submission_ref.save()
        else:
            self.assignment_ref.total_marks = 100
            self.submission_ref.marks = round((scored / count) * 100, 2)
            self.assignment_ref.save()
            self.submission_ref.save()


# ------------------------------------------------------------


class Submission_MCQ_View(APIView):

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
            submission_de_serialized = SubmissionMCQ_Serializer(data=request.data)
            submission_de_serialized.initial_data["user_ref"] = int(isAuthorizedUSER[1])
            if submission_de_serialized.is_valid():
                submission_de_serialized.save()
                auto_mark = Auto_Mark_MCQ(submission_de_serialized.data["id"])
                auto_mark.start()
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
                            submission_ref_list = SubmissionMCQ.objects.filter(user_ref=isAuthorizedUSER[1])
                            data["success"] = True
                            data["data"] = [SubmissionMCQ_Serializer(one, many=False).data for one in submission_ref_list]
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:  # TODO : Specific Submission
                            try:
                                submission_ref = SubmissionMCQ.objects.get(user_ref=isAuthorizedUSER[1], pk=int(pkk))
                            except SubmissionMCQ.DoesNotExist:
                                data["success"] = False
                                data["message"] = "INVALID_SUBMISSION_ID"
                                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                data["success"] = True
                                data["data"] = SubmissionMCQ_Serializer(submission_ref, many=False).data
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
                                            "submission": SubmissionMCQ_Serializer(
                                                SubmissionMCQ.objects.filter(assignment_ref=one), many=True
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
                                            "submission": SubmissionMCQ_Serializer(
                                                SubmissionMCQ.objects.filter(assignment_ref=int(pkk)), many=True
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
                                    submission_ref = SubmissionMCQ.objects.get(pk=int(pkk))
                                except SubmissionMCQ.DoesNotExist:
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
                                            data["data"] = SubmissionMCQ_Serializer(submission_ref, many=False).data
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
                    submission_ref = SubmissionMCQ.objects.get(user_ref=isAuthorizedUSER[1], pk=pk)
                except SubmissionMCQ.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_SUBMISSION_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    submission_serialized = SubmissionMCQ_Serializer(submission_ref, data=request.data)
                    submission_serialized.initial_data["user_ref"] = isAuthorizedUSER[1]
                    if submission_serialized.is_valid():
                        submission_serialized.save()
                        auto_mark = Auto_Mark_MCQ(submission_serialized.data["id"])
                        auto_mark.start()
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
                    submission_ref = SubmissionMCQ.objects.get(user_ref=isAuthorizedUSER[1], pk=pk)
                except SubmissionMCQ.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_SUBMISSION_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
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
            "body": "JSON DATA",
        }
        temp["GET"] = None
        temp["PUT"] = {
            "assignment_ref": "Number [FK]",
            "body": "JSON DATA",
        }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
