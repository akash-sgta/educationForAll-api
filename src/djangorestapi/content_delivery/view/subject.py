from django.http.response import JsonResponse

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from content_delivery.models import (
    Coordinator,
    Subject,
    Subject_Coordinator,
)
from content_delivery.serializer import (
    Subject_Serializer,
)

from auth_prime.important_modules import (
    am_I_Authorized,
    do_I_Have_Privilege,
)

# ------------------------------------------------------------


class Subject_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None):  # TODO : Only Admins with SAGP Privilege can create subjects
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
            if am_I_Authorized(request, "ADMIN") < 1:
                data["success"] = False
                data["message"] = f"USER_NOT_ADMIN"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if not do_I_Have_Privilege(request, "SAGP"):
                    data["success"] = False
                    data["message"] = f"ADMIN_DOES_NOT_HAVE_SAGP_PRIVILEGE"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    subject_de_serialized = Subject_Serializer(data=request.data)
                    details = " ".join([word.upper() for word in subject_de_serialized.initial_data["name"].split()])
                    try:
                        subject_ref = Subject.objects.get(name__icontains=details)
                    except Subject.DoesNotExist:
                        subject_de_serialized.initial_data["name"] = details
                        if subject_de_serialized.is_valid():
                            subject_de_serialized.save()
                            data["success"] = True
                            data["data"] = subject_de_serialized.data
                            return Response(data=data, status=status.HTTP_201_CREATED)
                        else:
                            data["success"] = False
                            data["message"] = subject_de_serialized.errors
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data["success"] = True
                        data["message"] = "SUBJECT_ALREADY_EXISTS"
                        data["data"] = Subject_Serializer(subject_ref, many=False).data
                        return Response(data=data, status=status.HTTP_409_CONFLICT)

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
                if int(pk) == 0:  # TODO: Universal asking for all subjects
                    data["data"] = Subject_Serializer(Subject.objects.all(), many=True).data
                    data["success"] = True
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
                elif int(pk) == 87795962440396049328460600526719:  # TODO: Coordinator asking for subjects to form post
                    try:
                        coordinator_ref = Coordinator.objects.get(user_ref=isAuthorizedUSER[1])
                    except Coordinator.DoesNotExist:
                        data["success"] = True
                        data["message"] = "USER_NOT_COORINATOR"
                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        subject_coordinator_ref = Subject_Coordinator.objects.filter(coordinator_ref=coordinator_ref)
                        data["success"] = True
                        data["data"] = [Subject_Serializer(one.subject_ref, many=False).data for one in subject_coordinator_ref]
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                else:  # TODO : User asking for specific subjects
                    try:
                        subject_ref = Subject.objects.get(pk=int(pk))
                    except Subject.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_SUBJECT_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        data["success"] = True
                        data["data"] = Subject_Serializer(subject_ref, many=False).data
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/content/subject/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):  # TODO : Only Admins with SAGP Privilege can edit subjects
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
                if am_I_Authorized(request, "ADMIN") < 1:
                    data["success"] = False
                    data["message"] = f"USER_NOT_ADMIN"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if not do_I_Have_Privilege(request, "SAGP"):
                        data["success"] = False
                        data["message"] = f"ADMIN_DOES_NOT_HAVE_CAGP_PRIVILEGE"
                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        try:
                            subject_ref = Subject.objects.get(subject_ref=int(pk))
                        except Subject.DoesNotExist:
                            data["success"] = False
                            data["message"] = "INVALID_SUBJECT_ID"
                            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            subject_de_serialized = Subject_Serializer(subject_ref, data=request.data)
                            details = " ".join([word.upper() for word in subject_de_serialized.initial_data["name"].split()])
                            try:
                                Subject.objects.get(name__icontains=details)
                            except Subject.DoesNotExist:
                                flag = True
                            else:
                                if subject_ref.pk != int(pk):
                                    flag = False
                                else:
                                    flag = True
                            finally:
                                if not flag:
                                    data["success"] = False
                                    data["message"] = "SUBJECT_NAME_ALREADY_IN_USE"
                                    return Response(data=data, status=status.HTTP_403_FORBIDDEN)
                                else:
                                    subject_de_serialized.initial_data["name"] = details
                                    if subject_de_serialized.is_valid():
                                        subject_de_serialized.save()
                                        data["success"] = True
                                        data["data"] = subject_de_serialized.data
                                        return Response(data=data, status=status.HTTP_201_CREATED)
                                    else:
                                        data["success"] = False
                                        data["message"] = subject_de_serialized.errors
                                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/content/subject/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):  # TODO : Only Admins with SAGP Privilege can delete subjects
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
                if am_I_Authorized(request, "ADMIN") < 1:
                    data["success"] = False
                    data["message"] = f"USER_NOT_ADMIN"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if not do_I_Have_Privilege(request, "SAGP"):
                        data["success"] = False
                        data["message"] = f"ADMIN_DOES_NOT_HAVE_CAGP_PRIVILEGE"
                        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        if int(pk) == 0:  # TODO : Delete all subjects
                            Subject.objects.all().delete()
                            data["success"] = True
                            data["message"] = "ALL_SUBJECTS_DELETED"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:  # TODO : Delete selected subjects
                            try:
                                subject_ref = Subject.objects.get(pk=int(pk))
                            except Subject.DoesNotExist:
                                data["success"] = False
                                data["message"] = "INVALID_SUBJECT_ID"
                                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                subject_ref.delete()
                                data["success"] = True
                                data["message"] = "SUBJECT_DELETED"
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/content/subject/<id>"}
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

        data["name"] = "Subject"

        temp["POST"] = {"name": "String : 128", "description": "String : unl"}
        temp["GET"] = None
        temp["PUT"] = {"name": "String : 128", "description": "String : unl"}
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
