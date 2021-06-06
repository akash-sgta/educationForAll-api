import re
import threading

from analytics.models import Permalink
from auth_prime.important_modules import am_I_Authorized, random_generator
from content_delivery.models import Coordinator, Lecture
from content_delivery.serializer import Lecture_Serializer
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

# ------------------------------------------------------------


class Clear_Permalink(threading.Thread):
    def __init__(self, name):
        super().__init__(name=f"PERML_{name}")
        self.pk = int(name)

    def run(self):
        Permalink.objects.filter(ref__exact={"class": str(Lecture), "pk": self.pk}).delete()


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
        profile = Lecture_Serializer(
            Lecture.objects.get(pk=self.pk), data=Lecture_Serializer(Lecture.objects.get(pk=self.pk), many=False).data
        )

        if profile.initial_data["external_url_1"] not in (None, ""):
            if not self.check(profile.initial_data["external_url_1"]):
                permalink_ref = Permalink(
                    ref={"class": str(Lecture), "pk": profile.initial_data["id"]},
                    name=random_generator(16),
                    body=profile.initial_data["external_url_1"],
                )
                permalink_ref.save()
                profile.initial_data["external_url_1"] = f"/api/analytics/perm/{permalink_ref.name}"

        if profile.initial_data["external_url_2"] not in (None, ""):
            if not self.check(profile.initial_data["external_url_2"]):
                permalink_ref = Permalink(
                    ref={"class": str(Lecture), "pk": profile.initial_data["id"]},
                    name=random_generator(16),
                    body=profile.initial_data["external_url_2"],
                )
                permalink_ref.save()
                profile.initial_data["external_url_2"] = f"/api/analytics/perm/{permalink_ref.name}"

        if profile.is_valid():
            profile.save()
        else:
            print(profile.errors)


class Lecture_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None):  # TODO : Only Coordinator can create lecture
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
                lecture_de_serialized = Lecture_Serializer(data=request.data)
                if lecture_de_serialized.is_valid():
                    lecture_de_serialized.save()

                    Set_Permalink(lecture_de_serialized.data["id"]).start()

                    data["success"] = True
                    data["data"] = lecture_de_serialized.data
                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    data["success"] = False
                    data["message"] = lecture_de_serialized.errors
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):  # TODO : See all access granted to no one--# FIX : See if changes needed
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
                    lecture_ref = Lecture.objects.get(pk=int(pk))
                except Lecture.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_FORUM_ID"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                else:
                    data["success"] = True
                    data["data"] = Lecture_Serializer(lecture_ref, many=False).data
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/content/lecture/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):  # TODO : Only Coordinator can create lecture
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
                        lecture_ref = Lecture.objects.get(pk=int(pk))
                    except Lecture.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_LECTURE_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        lecture_de_serialized = Lecture_Serializer(lecture_ref, data=request.data)
                        if lecture_de_serialized.is_valid():
                            lecture_de_serialized.save()

                            Clear_Permalink(lecture_de_serialized.data["id"]).start()
                            Set_Permalink(lecture_de_serialized.data["id"]).start()

                            data["success"] = True
                            data["data"] = lecture_de_serialized.data
                            return Response(data=data, status=status.HTTP_201_CREATED)
                        else:
                            data["success"] = False
                            data["message"] = lecture_de_serialized.errors
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/content/lecture/<id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):  # TODO : Only Coordinators can delete--# FIX : All delete given to no one
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
                        lecture_ref = Lecture.objects.get(pk=int(pk))
                    except Lecture.DoesNotExist:
                        data["success"] = False
                        data["message"] = "INVALID_LECTURE_ID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        Clear_Permalink(lecture_ref.pk).start()

                        lecture_ref.delete()
                        data["success"] = True
                        data["message"] = "LECTURE_DELETED"
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/content/lecture/<id>"}
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

        data["name"] = "Lecture"

        temp["POST"] = {"body": "String", "external_url_1": "String : 255 / null", "external_url_2": "String : 255 / null"}
        temp["GET"] = None
        temp["PUT"] = {"body": "String", "external_url_1": "String : 255 / null", "external_url_2": "String : 255 / null"}
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
