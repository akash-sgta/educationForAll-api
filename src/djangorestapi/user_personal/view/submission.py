from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from content_delivery.models import (
    Coordinator,
    Assignment,
    Subject_Coordinator,
    Post,
)
from content_delivery.serializer import Assignment_Serializer

from user_personal.models import (
    Submission,
)
from user_personal.serializer import Submission_Serializer

# ------------------------------------------------------------


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
            submission_de_serialized.initial_data["user_credential_id"] = int(isAuthorizedUSER[1])
            if submission_de_serialized.is_valid():
                submission_de_serialized.save()
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
                                assignment_ids = [
                                    int(one["assignment_ref"])
                                    for one in Post.objects.filter(subject_ref__in=subject_ids).values("assignment_ref")
                                ]
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
                                data["success"] = False
                                data["data"] = temp.copy()
                                return Response(data=data, status=status.HTTP_200_OK)
                        else:  # TODO : Specific Submission
                            try:
                                coordinator_id = Coordinator.objects.get(user_ref=isAuthorizedUSER[1]).pk
                            except Coordinator.DoesNotExist:
                                data["success"] = False
                                data["message"] = "USER_NOT_COORDINATOR"
                                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                            else:  # FIX : Place a checker for Coordinators checking only for their subjects
                                try:
                                    submission_ref = Submission.objects.get(pk=int(pkk))
                                except Submission.DoesNotExist:
                                    data["success"] = False
                                    data["message"] = "INVALID_SUBMISSION_ID"
                                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    subject_of_submission = int(
                                        Post.objects.get(assignment_ref=submission_ref.assignment_ref).subject_ref.pk
                                    )
                                    subjects_under_coordinator = [
                                        int(one["subject_ref"])
                                        for one in Subject_Coordinator.objects.filter(coordinator_ref=coordinator_id).values(
                                            "subject_ref"
                                        )
                                    ]
                                    if subject_of_submission in subjects_under_coordinator:
                                        data["success"] = True
                                        data["data"] = Submission_Serializer(submission_ref, many=False).data
                                        return Response(data=data, status=status.HTTP_200_OK)
                                    else:
                                        data["success"] = False
                                        data["message"] = "SUBMISSION_NOT_UNDER_COORDINATOR"
                                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
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

    def delete(self, request, pk_1=None, pk_2=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk_1 not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    submission_ref = Submission.objects.get(user_ref=isAuthorizedUSER[1], pk=pk_1)
                except Submission.DoesNotExist:
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
