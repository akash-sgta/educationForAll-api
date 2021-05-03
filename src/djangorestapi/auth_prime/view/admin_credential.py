from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from auth_prime.models import (
        User_Credential,
        Admin_Credential,
        Admin_Cred_Admin_Prev_Int,
        Admin_Privilege
    )
from auth_prime.serializer import (
        Admin_Credential_Serializer
    )

# ------------------------------------------------------------

class Admin_Credential_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def post(self, request, pk=None):
        data = dict()
        
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        isAuthorizedUSER = am_I_Authorized(request, "USER")
        if(isAuthorizedUSER[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
            if(isAuthorizedADMIN < 3):
                data['success'] = False
                data['message'] = "USER does not have required ADMIN PRIVILEGES"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                data = dict()
                id = request.data['user_id']
                try:
                    user_cred_ref = User_Credential.objects.get(user_credential_id = int(id))
                except User_Credential.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                else:
                    try:
                        admin_cred_ref = Admin_Credential.objects.get(user_credential_id = id)
                    except Admin_Credential.DoesNotExist:
                        data['success'] = True
                        admin_cred_ref_new = Admin_Credential(user_credential_id = user_cred_ref).save()
                        data['data'] = Admin_Credential_Serializer(admin_cred_ref_new, many=False).data
                        return Response(data = data, status=status.HTTP_201_CREATED)
                    else:
                        data['success'] = True
                        data['message'] = f"Admin already exists"
                        privileges = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_cred_ref.admin_credential_id)
                        priv_list = list()
                        for priv in privileges:
                            priv_list.append(priv.admin_privilege_id.admin_privilege_id)
                        data['success'] = True
                        data['data'] = {
                            "admin" : Admin_Credential_Serializer(admin_cred_ref, many=False).data,
                            "privilege" : priv_list
                        }
                        return Response(data = data, status=status.HTTP_201_CREATED)
    
    def get(self, request, pk=None):
        data = dict()
                
        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
        
        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data)
            else:
                if(am_I_Authorized(request, "ADMIN") < 3):
                    data['success'] = False
                    data['message'] = "USER does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        if(int(pk) == 0 or int(pk) == isAuthorizedUSER[1]): #self
                            admin_cred_ref = Admin_Credential.objects.get(user_credential_id = isAuthorizedUSER[1])
                            privileges = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_cred_ref.admin_credential_id)
                            priv_list = list()
                            for priv in privileges:
                                priv_list.append(priv.admin_privilege_id.admin_privilege_id)
                            data['success'] = True
                            data['data'] = {
                                "admin" : Admin_Credential_Serializer(admin_cred_ref, many=False).data,
                                "privilege" : priv_list
                            }
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            if(am_I_Authorized(request, 'ADMIN') > 0):
                                if(int(pk) == 666):
                                    admin_cred_ref_all = Admin_Credential.objects.all()
                                    total = list()
                                    for acr in admin_cred_ref_all:
                                        privileges = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = acr.admin_credential_id)
                                        priv_list = list()
                                        for priv in privileges:
                                            priv_list.append(priv.admin_privilege_id.admin_privilege_id)
                                        total.append({
                                            "admin" : Admin_Credential_Serializer(acr, many=False).data,
                                            "privilege" : priv_list.copy()
                                        })
                                    data['success'] = True
                                    data['data'] = total
                                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                                else:
                                    try:
                                        admin_cred_ref = Admin_Credential.objects.get(user_credential_id = pk)
                                    except Admin_Credential.DoesNotExist:
                                        data['success'] = False
                                        data['message'] = "item User does not have ADMIN Privilege"
                                        return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                                    else:
                                        privileges = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_cred_ref.admin_credential_id)
                                        priv_list = list()
                                        for priv in privileges:
                                            priv_list.append(priv.admin_privilege_id.admin_privilege_id)
                                        data['success'] = True
                                        data['data'] = {
                                                "admin" : Admin_Credential_Serializer(admin_cred_ref, many=False).data,
                                                "privilege" : priv_list.copy()
                                            }
                                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                            else:
                                data['success'] = False
                                data['message'] = "User does not have ADMIN privileges"
                                return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                    except Exception as ex:
                        print("EX : ", ex)
                        return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/admin/cred/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)

        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data)
            else:
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if(isAuthorizedADMIN < 3):
                    data['success'] = False
                    data['message'] = "USER does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    privilege = int(request.data['privilege'])
                    if(Admin_Credential.objects.get(user_credential_id = isAuthorizedUSER[1]).prime == False):
                        data['success'] = False
                        data['message'] = "Only ADMIN PRIME authorized to change PRIVILEGES"
                        return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        if(int(pk) in (0, isAuthorizedUSER[1])): 
                            if(privilege  > 0): #self change
                                many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(
                                                    admin_credential_id = Admin_Credential.objects.get(user_credential_id = isAuthorizedUSER[1]),
                                                    admin_privilege_id = privilege
                                                )
                                if(len(many_to_many) > 0):
                                    data['success'] = True
                                    data['message'] = "SELF : ADMIN already has the PRIVILEGE"
                                    return Response(data = data, status=status.HTTP_201_CREATED)
                                else:
                                    privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = privilege)
                                    if(len(privilege_ref) < 1):
                                        data['success'] = False
                                        data['message'] = "SELF :PRIVILEGE id invalid"
                                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                                    else:
                                        privilege_ref = privilege_ref[0]
                                        Admin_Cred_Admin_Prev_Int(
                                            admin_credential_id = Admin_Credential.objects.get(user_credential_id = isAuthorizedUSER[1]),
                                            admin_privilege_id = privilege_ref
                                        ).save()
                                        data['success'] = True
                                        data['message'] = "SELF : PRIVILEGE granted to ADMIN"
                                        return Response(data = data, status=status.HTTP_201_CREATED)
                            else: 
                                privilege = privilege*-1
                                many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(
                                                    admin_credential_id = Admin_Credential.objects.get(user_credential_id = isAuthorizedUSER[1]),
                                                    admin_privilege_id = privilege
                                                )
                                if(len(many_to_many) < 1):
                                    data['success'] = True
                                    data['message'] = "SELF : ADMIN does not the PRIVILEGE"
                                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                else:
                                    many_to_many[0].delete()
                                    data['success'] = True
                                    data['message'] = "SELF : PRIVILEGE revoked from ADMIN"
                                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
                        else: # change others
                            if(privilege  > 0):
                                try:
                                    many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(
                                                        admin_credential_id = Admin_Credential.objects.get(user_credential_id = int(pk)),
                                                        admin_privilege_id = privilege
                                                    )
                                except Admin_Credential.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = "item does not exist"
                                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    if(len(many_to_many) > 0):
                                        data['success'] = True
                                        data['message'] = "ADMIN already has the PRIVILEGE"
                                        return Response(data = data, status=status.HTTP_201_CREATED)
                                    else:
                                        privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = privilege)
                                        if(len(privilege_ref) < 1):
                                            data['success'] = False
                                            data['message'] = "PRIVILEGE id invalid"
                                            return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                                        else:
                                            privilege_ref = privilege_ref[0]
                                            Admin_Cred_Admin_Prev_Int(
                                                admin_credential_id = Admin_Credential.objects.get(user_credential_id = int(pk)),
                                                admin_privilege_id = privilege_ref
                                            ).save()
                                            data['success'] = True
                                            data['message'] = "PRIVILEGE granted to ADMIN"
                                            return Response(data = data, status=status.HTTP_201_CREATED)
                            else:
                                privilege = privilege*-1
                                try:
                                    many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(
                                                        admin_credential_id = Admin_Credential.objects.get(user_credential_id = int(pk)),
                                                        admin_privilege_id = privilege
                                                    )
                                except Admin_Credential.DoesNotExist:
                                    data['success'] = False
                                    data['message'] = "item does not exist"
                                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                                else:
                                    if(len(many_to_many) < 1):
                                        data['success'] = True
                                        data['message'] = "ADMIN does not the PRIVILEGE"
                                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
                                    else:
                                        many_to_many[0].delete()
                                        data['success'] = True
                                        data['message'] = "PRIVILEGE revoked from ADMIN"
                                        return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/admin/cred/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)

        if(pk not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data)
            else:
                isAuthorizedADMIN = am_I_Authorized(request, "ADMIN")
                if(isAuthorizedADMIN < 3):
                    data['success'] = False
                    data['message'] = "USER does not have required ADMIN PRIVILEGES"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        if(int(pk) == 0 or int(pk) == isAuthorizedUSER[1]): #self
                            Admin_Credential.objects.get(user_credential_id = isAuthorizedUSER[1]).delete()
                            data['success'] = True
                            data['message'] = "Admin Profile deleted"
                            return Response(data = data, status = status.HTTP_202_ACCEPTED)
                        else:
                            if(am_I_Authorized(request, 'ADMIN') > 0):
                                if(int(pk) == 666):
                                    Admin_Credential.objects.all().exclude(user_credential_id = isAuthorizedUSER[1]).delete()
                                    data['success'] = True
                                    data['message'] = "All Admin Profile(s) Deleted"
                                    return Response(data = data, status = status.HTTP_202_ACCEPTED)
                                else:
                                    try:
                                        admin_cred_ref = Admin_Credential.objects.get(user_credential_id = pk)
                                    except Admin_Credential.DoesNotExist:
                                        data['success'] = False
                                        data['message'] = "item invalid"
                                        return Response(data = data, status = status.HTTP_404_NOT_FOUND)
                                    else:
                                        admin_cred_ref.delete()
                                        data['success'] = True
                                        data['message'] = "Admin Profile deleted"
                                        return Response(data = data, status = status.HTTP_202_ACCEPTED)
                            else:
                                data['success'] = False
                                data['message'] = "User does not have ADMIN privileges"
                                return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
                    except Exception as ex:
                        print("EX : ", ex)
                        return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'DELETE',
                'URL_FORMAT' : '/api/admin/cred/<id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if(not isAuthorizedAPI[0]):
            data['success'] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            
        temp = dict()

        data["Allow"] = "POST GET PUT DELETE OPTIONS".split()
        
        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()
        
        data["name"] = "Admin_Credential"
        
        temp["POST"] = {
                "user_id" : "Number"
            }
        temp["GET"] = None
        temp["PUT"] = {
                "privilege" : "Number"
            }
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
