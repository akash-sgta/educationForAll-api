from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser

from auth_prime.models import (
        Api_Token_Table,
        User_Token_Table,
        Admin_Credential,
        Admin_Privilege,
        Admin_Cred_Admin_Prev_Int
    )

from hashlib import sha256
import string
import random

# --------------------------------------------------------

def am_I_Authorized(request, key):
    
    if(key.lower() == 'api'):
        try:
            headers = request.headers
            if('Authorization' in headers):
                token = headers['Authorization'].split()[1]
                api_token_ref = Api_Token_Table.objects.filter(user_key_private = token)
                if(len(api_token_ref) < 1):
                    return (False, "API_KEY_UNAUTHORIZED")
                else:
                    api_token_ref = api_token_ref[0]
                    return (True, f"USER - {api_token_ref.user_name}")
            else:
                return (False, "HTTP_Header_Mismatch - Authorization")
        except Exception as ex:
            print("EX : ", ex)
            return (False, "HTTP_Header_Mismatch - Authorization")
    
    elif(key.lower() == 'user'):
        try:
            headers = request.headers
            if('uauth' in headers):
                token = headers['uauth'].split()[1]
                user_token_ref = User_Token_Table.objects.filter(token_hash = token)
                if(len(user_token_ref) < 1):
                    return (False, "USER_HASH_UNAUTHORIZED")
                else:
                    user_token_ref = user_token_ref[0]
                    return (True, user_token_ref.user_credential_id.user_credential_id)
            else:
                return (False, "HTTP_Header_Mismatch - uauth")
        except Exception as ex:
            print("EX : ", ex)
            return (False, "HTTP_Header_Mismatch - uauth")
    
    elif(key.lower() == 'admin'): # todo
        try:
            headers = request.headers
            if('uauth' in headers):
                token = headers['uauth'].split()[1]
                user_token_ref = User_Token_Table.objects.filter(token_hash = token)
                if(len(user_token_ref) < 1):
                    return 0
                else:
                    user_token_ref = user_token_ref[0]
                    admin_cred_ref = Admin_Credential.objects.filter(
                                        user_credential_id = user_token_ref.user_credential_id.user_credential_id
                                    )
                    if(len(admin_cred_ref) < 1):
                        return 0
                    else:
                        if(admin_cred_ref[0].prime == False):
                            return 2
                        else:
                            return 3 # for now, later check admin level
            else:
                return 0
                
        except Exception as ex:
            print("EX : ", ex)
            return 0

def do_I_Have_Privilege(request, key):

    try:
        headers = request.headers
        if('uauth' in headers):
            token = headers['uauth'].split()[1]
            user_token_ref = User_Token_Table.objects.filter(token_hash = token)
            if(len(user_token_ref) < 1):
                return False
            else:
                user_token_ref = user_token_ref[0]
                admin_cred_ref = Admin_Credential.objects.filter(
                                    user_credential_id = user_token_ref.user_credential_id.user_credential_id
                                )
                if(len(admin_cred_ref) < 1):
                        return False
                else:
                    privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name = key.upper())
                    if(len(privilege_ref) < 1):
                        return False
                    else:
                        many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(
                                            admin_credential_id = admin_cred_ref[0].admin_credential_id,
                                            admin_privilege_id = privilege_ref[0].admin_privilege_id
                                        )
                        if(len(many_to_many_ref) < 1):
                            return False
                        else:
                            return True
        else:
            return False
    except Exception as ex:
        print("EX : ", ex)
        return False

def create_password_hashed(password):
    sha256_ref = sha256()
    sha256_ref.update(f"ooga{password}booga".encode('utf-8'))
    return str(sha256_ref.digest())

def random_generator(length=64):
    password_characters = string.ascii_letters + string.digits
    password = list()
    for x in range(length):
        password.append(random.choice(password_characters))
        
    return "".join(password)

def create_token(user_cred_ref):
    user_token_ref = User_Token_Table.objects.filter(user_credential_id = user_cred_ref.user_credential_id)
    if(len(user_token_ref) < 1):
        user_token_ref = User_Token_Table(
            user_credential_id = user_cred_ref,
            token_hash = random_generator()
        )
        user_token_ref.save()
    else:
        user_token_ref = user_token_ref[0]
    return user_token_ref.token_hash

# --------------------------------------------------------

def logger(api_key, message):
    import logging
    logging.basicConfig(filename="api_access.log", filemode="w", format='%(asctime)s | %(message)s')
    logging.warning(f"{api_key} -> {message}")

class Json_Forward(object):

    def __init__(self):
        super().__init__()
    
    # true call return
    def TRUE_CALL(self, data=None, message=None):
        if(data != None):
            if(message != None):
                return {"return" : True, "code" : 100, "data" : data, "message" : message}
            else:
                return {"return" : True, "code" : 100, "data" : data}
        elif(message != None):
            return {"return" : True, "code" : 100, "message" : message}
        else:
            return {"return" : True, "code" : 100}

    # invalid GET method
    def GET_INVALID(self, data=None):
        return {"return" : False, "code" : 403, "message" : 'ERROR-Invalid-GET Not supported'}

    # JSONParser error
    def JSON_PARSER_ERROR(self, data):
        return {"return" : False, "code" : 401, "message" : f"ERROR-Parsing-{str(data)}"}

    # missing KEY
    def MISSING_KEY(self, data):
        return {"return" : False, "code" : 402, "message" : f"ERROR-Key-{str(data)}"}

    # invalid API
    def API_RELATED(self, data):
        return {"return" : False, "code" : 115, "message" : f"ERROR-Key-{str(data)}"}

    # error ambiguous 404
    def AMBIGUOUS_404(self, data):
        return {"return" : False, "code" : 404, "message" : f"ERROR-Ambiguous-{str(data)}"}

    # invalid action
    def INVALID_ACTION(self, data):
        if(str(data).upper() == 'PARENT'):
            return {"return" : False, "code" : 403, "message" : "ERROR-Action-Child action invalid"}
        elif(str(data).upper() == 'CHILD'):
            return {"return" : False, "code" : 403, "message" : "ERROR-Action-Parent action invalid"}
        else:
            return {"return" : False, "code" : 403, "message" : f"ERROR-Action-{str(data).upper()} action invalid"}

    # custom error reference
    def CUSTOM_FALSE(self, code=None, message=None):
        if(code != None and message != None):
            return {"return" : False, "code" : code, "message" : f"ERROR-{message}"}
        else:
            return {"return" : False, "code" : None, "message" : "Custom_False:Admin"}

class API_Prime(Json_Forward):

    def __init__(self):
        super().__init__()
        self.__request = None
        self.__data_returned = dict()
        self.json_response = JsonResponse({"return" : False, "message" : "Action not permitted"}, safe=True)
    
    @property
    def request(self):
        return self.__request
    @request.setter
    def request(self, data):
        self.__request = data
    
    @property
    def data_returned(self):
        return self.__data_returned
    @data_returned.setter
    def data_returned(self, data):
        self.__data_returned = data
    
    def method_get(self):
        return JsonResponse(self.GET_INVALID(), safe=True)
    
    def create(self, *args, **kwargs):
        return self.json_response
    
    def read(self, *args, **kwargs):
        return self.json_response
    
    def edit(self, *args, **kwargs):
        return self.json_response
    
    def delete(self, *args, **kwargs):
        return self.json_response
    
    def method_post(self):
        try:
            user_data = JSONParser().parse(self.request)

        except Exception as ex:
            return JsonResponse(self.JSON_PARSER_ERROR(ex), safe=True)
                
        else:
            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]
                # print(incoming_data)

            except Exception as ex:
                return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
            else:
                self.api = incoming_api
                data = self.check_authorization(api_check=True)
                if(data[0] == False):
                    return JsonResponse(self.API_RELATED(data[1]), safe=True)

                else:
                    try:
                        child_method = incoming_data["action"].upper()
                        if(child_method == "CREATE"):
                            return self.create(incoming_data)
                        
                        elif(child_method == 'READ'):
                            return self.read(incoming_data)
                        
                        elif(child_method == 'EDIT'):
                            return self.edit(incoming_data)
                        
                        elif(child_method == 'DELETE'):
                            return self.delete(incoming_data)

                        else:
                            return JsonResponse(self.INVALID_ACTION('child'), safe=True)
                    
                    except Exception as ex:
                        return JsonResponse(self.AMBIGUOUS_404(ex), safe=True)

    @csrf_exempt
    def run(self, request = None):
        if(request == None):
            raise Exception('[request] not passed as argument')
 
        else:
            self.request = request
            parent_method = self.request.method.upper()
            self.data_returned['action'] = parent_method
            if(parent_method == 'GET'):
                return self.method_get()

            elif(parent_method == 'POST'):
                return self.method_post()

            else:
                return JsonResponse(self.INVALID_ACTION('parent'), safe=True)

    def __str__(self):
        return super().__str__()
