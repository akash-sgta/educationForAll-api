from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from user_personal.models import Enroll
from user_personal.serializer import Enroll_Serializer

from content_delivery.models import Coordinator, Subject_Coordinator

# ------------------------------------------------------------


class Enroll_View(APIView):

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
                enroll_ref = Enroll.objects.get(user_ref=isAuthorizedUSER[1], subject_ref=request.data["subject_id"])
            except Enroll.DoesNotExist:
                enroll_de_serialized = Enroll_Serializer(data=request.data)
                enroll_de_serialized.initial_data["user_ref"] = int(isAuthorizedUSER[1])
                if enroll_de_serialized.is_valid():
                    enroll_de_serialized.save()
                    data["success"] = True
                    data["data"] = enroll_de_serialized.data
                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    data["success"] = False
                    data["message"] = f"SERIALIZING_ERROR : {enroll_de_serialized.errors}"
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data["success"] = True
                data["message"] = f"USER_ALREADY_ENROLLED"
                data["data"] = Enroll_Serializer(enroll_ref, many=False).data
                return Response(data=data, status=status.HTTP_202_ACCEPTED)

    def get(self, request, pk=None):
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
                    if int(pk) == 87795962440396049328460600526719:  # TODO : Coordinator Looking for their enrollments
                        try:
                            coordinator_ref = Coordinator.objects.get(user_ref=isAuthorizedUSER[1])
                        except Coordinator.DoesNotExist:
                            data["success"] = False
                            data["message"] = "USER_NOT_COORDINATOR"
                            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            subjects = [
                                one["subject_ref"]
                                for one in Subject_Coordinator.objects.filter(coordinator_ref=coordinator_ref).values(
                                    "subject_ref"
                                )
                            ]
                            data["data"] = list()
                            for one in subjects:
                                data["data"].append(
                                    {
                                        "subject": one,
                                        "user": [
                                            enroll["user_ref"]
                                            for enroll in Enroll.objects.filter(subject_ref=one).values("user_ref")
                                        ],
                                    }
                                )
                            data["success"] = True
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    elif int(pk) == 0:  # TODO : User looking for their enrollment
                        data["success"] = True
                        data["data"] = {
                            "subject": [
                                one["subject_ref"]
                                for one in Enroll.objects.filter(user_ref=isAuthorizedUSER[1]).values("subject_ref")
                            ]
                        }
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                except Exception as ex:
                    print("ENROLL_GET EX : ", ex)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/personal/enroll/<id>"}
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
                    enroll_ref = Enroll.objects.get(user_ref=isAuthorizedUSER[1], subject_ref=pk)
                except Enroll.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_ENROLLMENT_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    enroll_ref.delete()
                    data["success"] = True
                    data["message"] = "ENROLLMENT_DELETED"
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/personal/enroll/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        temp = dict()

        data["Allow"] = "POST GET DELETE OPTIONS".split()

        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()

        data["name"] = "Enroll"

        temp["POST"] = {"subject_id": "Number"}
        temp["GET"] = None
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
