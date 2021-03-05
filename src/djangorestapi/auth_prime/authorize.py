class Authorize_Prime(object):
    
    def __init__(self, user_credential_id=None, user_email=None, user_password=None, token=None):
        super().__init__()
        self._user_credential_id = user_credential_id
        self._user_email = user_email
        self._user_password = user_password
        self._token = token
    
    @property
    def user_credential_id(self):
        return self._user_credential_id
    @user_credential_id.setter
    def user_credential_id(self, data):
        from auth_prime.models import User_Credential
        
        if(len(User_Credential.objects.filter(user_credential_id = int(data))) > 0):
            self._user_credential_id = data
        else:
            raise Exception("[x] User Id not found in DB.")
    
    @property
    def user_email(self):
        return self._user_email
    @user_email.setter
    def user_email(self, data):
        import re
        PATTERN = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if(re.search(PATTERN, data)):
            self._user_email = data
        else:
            raise Exception("[x] Wrong email format.")
    
    @property
    def user_password(self):
        return self._user_password
    @user_password.setter
    def user_password(self, data):
        import re
        PATTERN = r'^[a-zA-Z0-9_]{8,}$'
        if(re.search(PATTERN, data)):
            self._user_password = data
        else:
            raise Exception("Password must be more than 8 characters. [a-zA-Z0-9_]")
    
    @property
    def token(self):
        return self._token
    @token.setter
    def token(self, data):
        self._token = data

    def clear(self):
        self._user_credential_id = None
        self._user_email = None
        self._user_password = None
        self._token = None
    
    def create_token(self):
        if((self.user_email == None) or (self.user_password == None)):
            return {"returned":False, "message":"Initialize email and password"}
        else:
            from auth_prime.models import User_Credential
            from hashlib import sha256

            data = self.create_password_hashed()
            user_credential_ref = User_Credential.objects.filter(user_email = self.user_email)
            
            if(len(user_credential_ref) < 1):
                return {"returned":False, "message":"Wrong Email."}
            else:
                user_credential_ref = user_credential_ref[0]
                
                if(user_credential_ref.user_password != data[1]):
                    return {"returned":False, "message":"Wrong Password."}
                else:
                
                    from auth_prime.models import User_Token_Table
                    from datetime import datetime, timedelta

                    user_credential_id = user_credential_ref.user_credential_id

                    now = datetime.now()
                    then = now + timedelta(hours=24)
                    now = now.strftime("%d-%m-%Y %H:%M:%S")
                    then = then.strftime("%d-%m-%Y %H:%M:%S")
                    
                    token_hash = self.random_generator()
                    
                    try:
                        user_credential_id = User_Credential.objects.get(user_credential_id=user_credential_id)
                        token_table_ref = User_Token_Table.objects.filter(user_credential_id = user_credential_id)
                        if(len(token_table_ref) < 1):
                            token_table_ref = User_Token_Table(user_credential_id = user_credential_id,
                                                        token_hash = token_hash,
                                                        token_start = now,
                                                        token_end = then)
                            token_table_ref.save()
                        else:
                            token_table_ref = token_table_ref[0]
                            token_hash = token_table_ref.token_hash
                    except Exception as ex:
                        return {"returned":False, "message":f"{str(ex)}"}
                    else:
                        return {"returned":True, "message":"Successful Token Generation.", "data":token_hash}

    def check_token(self):
        if(self.token == None):
            return {"returned":False, "message":"Initialize token."}
        else:
            from auth_prime.models import User_Token_Table

            token_table_ref = User_Token_Table.objects.filter(token_hash = self.token)
            if(len(token_table_ref) < 1):
                self._token = None
                return {"returned":False, "message":"Token not found in DB."}
            else:
                token_table_ref = token_table_ref[0]
                return {"returned":True, "message":"Successful Token Check.", "data":token_table_ref.user_credential_id.user_credential_id}
    
    def remove_token(self):
        if(self.token == None):
            return {"returned":False, "message":"Initialize token."}
        else:
            from auth_prime.models import User_Token_Table

            token_table_ref = User_Token_Table.objects.filter(token_hash = self.token)
            if(len(token_table_ref) < 0):
                self._token = None
                return {"returned":False, "message":"Token not found in DB."}
            else:
                token_table_ref = token_table_ref[0]
                token_table_ref.delete()
                return {"returned":True, "message":"Successful Token Removal."}

    def create_password_hashed(self):
        if(self.user_password == None):
            return False,"Initialize Password"
        else:
            from hashlib import sha256
            sha256_ref = sha256()
            sha256_ref.update(f"ooga{self.user_password}booga".encode('utf-8'))
            return True,str(sha256_ref.digest())

    def random_generator(self, l=64):
        import string
        import random

        password_characters = string.ascii_letters + string.digits
        password = []
        for x in range(l):
            password.append(random.choice(password_characters))
        
        return "".join(password)

class Authorize(Authorize_Prime):

    def __init__(self, user_credential_id=None, user_email=None, user_password=None, token=None):
        super().__init__(user_credential_id=user_credential_id, user_email=user_email, user_password=user_password, token=token)
        self.__api_auth = None
        self.__api_version_u = None
        self.__api_version = "1.0"
    
    @property
    def api_auth(self):
        return self.__api_auth
    @api_auth.setter
    def api_auth(self, data):
        self.__api_auth = data
    
    @property
    def api_version(self):
        return self.__api_version_u
    @api_version.setter
    def api_version(self, data):
        self.__api_version_u = data
    
    @property
    def api(self):
        return {"version" : self.api_version, "auth" : self.api_auth}
    @api.setter
    def api(self, data):
        try:
            self.api_auth = data['auth']
            self.api_version = data['version']
        except:
            raise Exception("Check API Contract for API_AUTH attributes.")
    

    
    def check_authorization(self, key_1=None, key_2=None, api_check=False):
        from auth_prime.models import Admin_Credential
        from auth_prime.models import Admin_Privilege
        from auth_prime.models import Admin_Cred_Admin_Prev_Int

        from auth_prime.models import User_Credential
        from auth_prime.models import Api_Token_Table

        def logger(api_key, message=None):
            try:
                import logging
                logging.basicConfig(format='%(asctime)s -- %(message)s')
                logging.warning(f"API : {api_key} | {message}")
            except Exception:
                return False
            else:
                return True

        if(api_check == False):
            data = self.check_token()

            if(data['returned'] == False):
                print("[x] CHECK_TOKEN - {}".format(data['message'])) #check here
                rdata = (False, data['message'])
            
            else:
                if(key_1 != None):
                    
                    if(key_1.upper() == "USER"):
                        rdata = (True, data["data"])
                
                    elif(key_1.upper() == "ADMIN"):

                        user_credential_ref = User_Credential.objects.get(user_credential_id = int(data['data']))
                        admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = user_credential_ref)
                        if(len(admin_credential_ref) > 0):
                            admin_credential_ref = admin_credential_ref[0]

                            if(key_2 != None and key_2.upper() == "PRIME"):
                                # hash - true
                                # user is admin - true
                                if(admin_credential_ref.prime == True):
                                    rdata = (True, int(data['data'])) # sending back hash related user data
                                else:
                                    message = "ADMIN not PRIME."
                                    print("[x] CHECK_TOKEN_ADMIN - {}".format(message))
                                    rdata = (False, message)
                            
                            elif(key_2 != None and key_2.upper() == 'ALPHA'):
                                admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__icontains = 'ALPHA')

                                if(len(admin_privilege_ref) < 1):
                                    rdata = (False, "AdminPriv-ALPHA not found")
                                        
                                else:
                                    admin_privilege_ref = admin_privilege_ref[0]
                                    many_to_many = Admin_Cred_Admin_Prev_Int.objects.filter(admin_privilege_id = admin_privilege_ref.admin_privilege_id,
                                                                                            admin_credential_id = admin_credential_ref.admin_credential_id)
                                            
                                    if(len(many_to_many) < 1):
                                        rdata = (False, "Pair-Admin Credential<+>Admin Privilege not found")
                                    else:
                                        rdata = (True, int(data['data'])) # sending back hash related user data
                            
                            elif(key_2 != None and key_2.upper() == 'CAGP'):
                                admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = 'CAGP') # for COPG privilege exists
                                    
                                if(len(admin_privilege_ref) < 1):
                                    rdata = (False, 'NotFound-CAGP privilege')
                                    
                                else:
                                    admin_privilege_ref = admin_privilege_ref[0]
                                    many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id,
                                                                                                admin_privilege_id = admin_privilege_ref.admin_privilege_id) # for the hash admin has the privilege
                                        
                                    if(len(many_to_many_ref) < 1):
                                        rdata = (False, "Pair-Not Found Admin Credential<=>Admin PRIVILEGE")

                                    else:
                                        rdata = (True, int(data['data'])) # sending back hash related user data

                            else:
                                # hash - true
                                # user is admin - true
                                rdata = (True, int(data['data'])) # sending back hash related user data
                        
                        else:
                            message = "USER not ADMIN."
                            print("[x] CHECK_TOKEN_ADMIN - {}".format(message))
                            rdata = (False, message)
                    
                    else:
                        rdata = (False, "[1] Check key_1 sent to is_authorized()")
                
                else:
                    rdata = (False, "[2] Check key_1 sent to is_authorized()")
            
            return rdata
        
        else:
            if(self.api_auth == None):
                rdata = (False, "Initialize API AUTH TOKEN.")
            else:
                try:
                    if(self.api_version != self.__api_version):
                        rdata = (False, "Invalid API Version specified.")
                    else:
                        api_ref = Api_Token_Table.objects.filter(user_key_private = self.api_auth)
                        if(len(api_ref) < 1):
                            rdata = (False, "Invalid API AUTH TOKEN")
                        else:
                            # print("LOGGER : ",logger(api_key = self.api_auth, message = api_ref[0].user_name))
                            rdata = (True, 1)
                except Exception as ex:
                    rdata = (False, str(ex))
            
            return rdata

    def sanction_authorization(self):

        data = self.create_token()
        if(data['returned'] == False):
            print("[x] CREATE_TOKEN - {}".format(data['message']))
            rdata =  (False, data['message'])
        else:
            rdata = (True, data['data'])
        
        return rdata
    
    def revoke_authorization(self):

        data = self.remove_token()
        if(data['returned'] == False):
            print("[x] REMOVE_TOKEN - {}".format(data['message']))
            rdata = (False, data['message'])
        else:
            rdata = (True, data['data'])
        
        return rdata

class Cookie(object):
    
    def __init__(self, hash=None):
        super().__init__()
        self._token = hash
    
    @property
    def token(self):
        return self._token
    @token.setter
    def token(self, data):
        self._token = data
    
    # ------------------------------------------
    # Cookie Push handle
    def setCookie(self, request, file_path=None, data=None, **kwargs):
        
        key_list = list(kwargs.keys())
        try:
            if((file_path == None) or (data == None)):
                raise Exception('Required Arguments not found.')
            else:
                from django.shortcuts import render
                import json

                request.session.set_expiry(0)
                response = render(request, file_path, data)
                for item in key_list:
                    if(item not in ('file_path','data')):
                        if(type(kwargs[item]) == type(dict())):
                            response.set_cookie(f"{item}", json.dumps(kwargs[item]))
                        else:
                            response.set_cookie(f"{item}", kwargs[item])

        except Exception as ex:
            print(f"[x] SET COOKIE Ex : {str(ex)}")
            return None
        else:
            return response
    # ------------------------------------------
    # Cookie Pull handle
    def getCookie(self, request, *args):

        try:
            cookies = list()
            for arg in args:
                temp = request.COOKIES[str(arg)]
                cookies.append(temp)
            return cookies
        except Exception as ex:
            print(f"[x] GET COOKIE Ex : {str(ex)}")
            cookies.append(None)
            return cookies
    # ------------------------------------------
    def make_hash(self, *args):

        try:
            from hashlib import sha256

            data = ""
            for arg in args:
                data += f'&{arg}'
            hashd = str(sha256(data.encode('utf-8')).digest())
        except Exception as ex:
            print(f"[x] HASH Ex : {str(ex)}")
            return None
        else:
            return hashd
    # ------------------------------------------
    def set_authentication_info(self, request=None, file_path=None, data=None, pk=None):
        
        try:
            if((file_path==None) or (data==None) or (pk==None)):
                raise Exception("Necessary arguments not passed.")
            else:
                from auth_prime.models import Api_Token_Table

                user = Api_Token_Table.objects.get(pk=pk)
                tauth = f"{user.pk}::{self.make_hash(user.user_email, user.user_password)}"
        except Exception as ex:
            from django.shortcuts import redirect

            print(f"[x] SET AUTH Ex : {str(ex)}")
            return redirect('API_TOKEN')
        else:
            return self.setCookie(request, file_path=file_path, data=data, tauth=tauth)

    # ------------------------------------------
    def revoke_authentication_info(self, request, file_path, data):
        
        try:
            if((file_path==None) or (data==None)):
                raise Exception("Necessary arguments not passed.")
            else:
                from django.shortcuts import render

                response = render(request, file_path, data)
                response.delete_cookie('tauth')
        except Exception as ex:
            from django.shortcuts import redirect

            print(f"[x] REVOKE AUTH  Ex : {str(ex)}")
            return redirect('forum_home')
        else:
            return response

    # ------------------------------------------
    def check_authentication_info(self, request):
        try:
            from auth_prime.models import Api_Token_Table

            user_credential = self.getCookie(request, 'tauth')
            # if auth false or not initialized
            if((user_credential[0] == None) or (user_credential[0] == False) or (user_credential[0] == "")):
                return False, 1
            else:
                cookie_user = user_credential[0].split("::")
                user = Api_Token_Table.objects.filter(pk = int(cookie_user[0]))
                if len(user) == 0:
                    return False, 2
                else:
                    user = user[0]
                    cookie_hash = cookie_user[1]
                    hash_check = self.make_hash(user.user_email, user.user_password)
                    if cookie_hash == hash_check:
                        return True, user.pk
                    else:
                        return False, 3
        except Exception as ex:
            print(f"[x] CHECK AUTH Ex : {str(ex)}")
            return False