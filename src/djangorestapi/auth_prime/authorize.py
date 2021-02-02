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
        self._user_password = data
    
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
            return {"returned":False, "message":"[x] Initialize email and password"}
        else:
            from auth_prime.models import User_Credential
            from hashlib import sha256

            data = self.create_password_hashed()
            user_credential_ref = User_Credential.objects.filter(user_email = self.user_email)
            
            if(len(user_credential_ref) < 1):
                return {"returned":False, "message":"[x] Wrong Email."}
            else:
                user_credential_ref = user_credential_ref[0]
                
                if(user_credential_ref.user_password != data[1]):
                    return {"returned":False, "message":"[x] Wrong Password."}
                else:
                
                    from auth_prime.models import Token_Table
                    from datetime import datetime, timedelta

                    user_credential_id = user_credential_ref.user_credential_id

                    now = datetime.now()
                    then = now + timedelta(hours=24)
                    now = now.strftime("%d-%m-%Y %H:%M:%S")
                    then = then.strftime("%d-%m-%Y %H:%M:%S")
                    
                    sha256_ref = sha256()
                    sha256_ref.update(f"{now}{self.user_email}{self.user_password}{then}".encode('utf-8'))
                    token_hash = str(sha256_ref.digest())
                    
                    try:
                        user_credential_id = User_Credential.objects.get(user_credential_id=user_credential_id)
                        token_table_ref = Token_Table.objects.filter(user_credential_id = user_credential_id)
                        if(len(token_table_ref) < 1):
                            token_table_ref = Token_Table(user_credential_id = user_credential_id,
                                                        token_hash = token_hash,
                                                        token_start = now,
                                                        token_end = then)
                            token_table_ref.save()
                        else:
                            token_table_ref = token_table_ref[0]
                            token_hash = token_table_ref.token_hash
                    except Exception as ex:
                        return {"returned":False, "message":f"[x] {ex}"}
                    else:
                        return {"returned":True, "message":"[.] Successful Token Generation.", "data":token_hash}

    def check_token(self):
        if(self.token == None):
            return {"returned":False, "message":"[x] Initialize token."}
        else:
            from auth_prime.models import Token_Table

            token_table_ref = Token_Table.objects.filter(token_hash = self.token)
            if(len(token_table_ref) < 1):
                self._token = None
                return {"returned":False, "message":"[x] Token not found in DB."}
            else:
                token_table_ref = token_table_ref[0]
                return {"returned":True, "message":"[.] Successful Token Check.", "data":token_table_ref.user_credential_id.user_credential_id}
    
    def remove_token(self):
        if(self.token == None):
            return {"returned":False, "message":"[x] Initialize token."}
        else:
            from auth_prime.models import Token_Table

            token_table_ref = Token_Table.objects.filter(token_hash = self.token)
            if(len(token_table_ref) < 0):
                self._token = None
                return {"returned":False, "message":"[x] Token not found in DB."}
            else:
                token_table_ref = token_table_ref[0]
                token_table_ref.delete()
                return {"returned":True, "message":"[.] Successful Token Removal."}

    def create_password_hashed(self):
        if(self.user_password == None):
            return False,"[x] Initialize Password"
        else:
            from hashlib import sha256
            sha256_ref = sha256()
            sha256_ref.update(f"ooga{self.user_password}booga".encode('utf-8'))
            return True,str(sha256_ref.digest())

class Authorize(Authorize_Prime):

    def __init__(self, user_credential_id=None, user_email=None, user_password=None, token=None):
        super().__init__(user_credential_id=user_credential_id, user_email=user_email, user_password=user_password, token=token)
    
    def is_authorized(self):
        import logging
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

        data = self.check_token()
        if(data['returned'] == False):
            logging.info("CHECK_TOKEN - "+data['message']) #check here
            return False,data['message']
        else:
            return True,data["data"]
    
    def sanction_authorization(self):
        import logging
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

        data = self.create_token()
        if(data['returned'] == False):
            logging.info("CREATE_TOKEN - "+data['message']) #check here
            return False,data['message']
        else:
            return True,data['data']
    
    def revoke_authorization(self):
        import logging
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

        data = self.remove_token()
        if(data['returned'] == False):
            logging.info("REMOVE_TOKEN - "+data['message']) #check here
            return False,data['message']
        else:
            return True,data['data']
    
    def is_authorized_admin(self):
        from auth_prime.models import Admin_Credential

        import logging
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

        data = self.check_token()
        if(data['returned'] == False):
            logging.info("CHECK_TOKEN_ADMIN - "+data['message']) #check here
            return False,data['message']
        else:
            admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(data['data']))
            if(len(admin_credential_ref) < 1):
                message = "[x] User not an ADMIN."
                logging.info("CHECK_TOKEN_ADMIN - "+message) #check here
                return False,message
            else:
                admin_credential_ref = admin_credential_ref[0]
                return True,admin_credential_ref.admin_credential_id
    
    def is_alpha_admin(self):
        from auth_prime.models import Admin_Credential

        data = self.is_authorized_admin()
        if(data[0] == False):
            return False, data[1]
        else:
            admin_credential_ref = Admin_Credential.objects.filter(admin_credential_id = int(data[1]))
            admin_credential_ref = admin_credential_ref[0]

            if(((admin_credential_ref.privilege_id_1 != None) and (admin_credential_ref.privilege_id_1.admin_privilege_id == 2))
            or ((admin_credential_ref.privilege_id_2 != None) and (admin_credential_ref.privilege_id_2.admin_privilege_id == 2))
            or ((admin_credential_ref.privilege_id_3 != None) and (admin_credential_ref.privilege_id_3.admin_privilege_id == 2))):

                return True, data[1]
            
            else:

                return False, "[x] Admin not having alpha privileges."
    
    
