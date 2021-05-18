from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
    am_I_Authorized,
)

from auth_prime.models import Privilege
from auth_prime.serializer import Privilege_Serializer

# ------------------------------------------------------------


class Admin_Privilege_View(APIView):

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
            isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
            if isAuthorizedADMIN != 69:  # TODO : Only ADMIN PRIME can create privileges
                data["success"] = False
                data["message"] = "ADMIN_NOT_ADMIN_PRIME"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    privilege_ref = Privilege.objects.get(name=request.data["name"].upper())
                except Privilege.DoesNotExist:
                    description = " ".join([word.capitalize() for word in request.data["description"].split()])
                    privilege_ref_new = Privilege(name=request.data["name"].upper(), description=description)
                    privilege_ref_new.save()
                    data["success"] = True
                    data["data"] = Privilege_Serializer(privilege_ref_new, many=False).data
                    return Response(data=data, status=status.HTTP_201_CREATED)
                else:
                    data["success"] = True
                    data["message"] = "PRIVILEGE_ALREADY_EXISTS"
                    data["data"] = Privilege_Serializer(privilege_ref, many=False).data
                    return Response(data=data, status=status.HTTP_201_CREATED)

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
                return Response(data=data)
            else:
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if isAuthorizedADMIN < 1:  # TODO : Any Admin can see privileges
                    data["success"] = False
                    data["message"] = "USER_NOT_ADMIN"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        if int(pk) == 0:  # TODO : Show all privileges
                            data["success"] = True
                            data["data"] = Privilege_Serializer(Privilege.objects.all(), many=True).data
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:  # TODO : Show specific privileges
                            try:
                                privilege_ref = Privilege.objects.get(pk=int(pk))
                            except Privilege.DoesNotExist:
                                data["success"] = False
                                data["message"] = "PRIVILEG_ID_INVALID"
                                return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                            else:
                                data["success"] = True
                                data["data"] = Privilege_Serializer(privilege_ref, many=False).data
                                return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    except Exception as ex:
                        print("ADMIN_PRIV_GET EX : ", ex)
                        return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/admin/priv/<id>"}
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
                return Response(data=data)
            else:
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if isAuthorizedADMIN != 69:  # TODO : Only Admin Prime has access to change privileges
                    data["success"] = False
                    data["message"] = "ADMIN_NOT_ADMIN_PRIME"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        privilege_ref = Privilege.objects.get(pk=pk)
                    except Privilege.DoesNotExist:
                        data["success"] = False
                        data["message"] = "PRIVILEG_ID_INVALID"
                        return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                    else:
                        privilege_de_serialized = Privilege_Serializer(privilege_ref, data=request.data)
                        if privilege_de_serialized.is_valid():
                            privilege_de_serialized.save()
                            data["success"] = True
                            data["data"] = privilege_de_serialized.data
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
                        else:
                            data["success"] = False
                            data["message"] = privilege_de_serialized.errors
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/admin/priv/<id>"}
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
                data["message"] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data=data)
            else:
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if isAuthorizedADMIN != 69:  # TODO : Only Admin Prime can delete admin privilege
                    data["success"] = False
                    data["message"] = "ADMIN_NOT_ADMIN_PRIME"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if int(pk) == 87795962440396049328460600526719:  # TODO : Delete all privileges
                        Privilege.objects.all().delete()
                        data["success"] = True
                        data["message"] = "ALL_ADMIN_PRIVILEGES_DELETED"
                        return Response(data=data, status=status.HTTP_202_ACCEPTED)
                    else:  # TODO : Delete selective privilges
                        try:
                            privilege_ref = Privilege.objects.get(pk=pk)
                        except Privilege.DoesNotExist:
                            data["success"] = False
                            data["message"] = "PRIVILEGE_ID_INVALID"
                            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                        else:
                            privilege_ref.delete()
                            data["success"] = True
                            data["message"] = "PRIVILEGE_DELETED"
                            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "DELETE", "URL_FORMAT": "/api/admin/priv/<id>"}
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

        data["name"] = "Admin_Privilege"

        temp["POST"] = {"name": "String : 32", "description": "String : unl"}
        temp["GET"] = None
        temp["PUT"] = {"name": "String : 32", "description": "String : unl"}
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
