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
        PATTERN = r'^[a-zA-Z0-9_~!@#$%^&*()_+]{8,}$'
        if(re.search(PATTERN, data)):
            self._user_password = data
        else:
            raise Exception("[x] Password must be more than 8 characters. [a-zA-Z0-9_~!@#$%^&*()_+]")
    
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
    
    def check_authorization(self, key_1=None, key_2=None):
        from auth_prime.models import Admin_Credential, User_Credential

        import logging
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

        data = self.check_token()

        if(data['returned'] == False):
            logging.info("CHECK_TOKEN - {}".format(data['message'])) #check here
            rdata = (False, data['message'])
        
        else:
            if(key_1 != None):
                
                if(key_1.upper() == "USER"):
                    rdata = (True, data["data"])
            
                elif(key_1.upper() == "ADMIN"):

                    user_credential_ref = User_Credential.objects.get(user_credential_id = int(data['data']))
                    admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = user_credential_ref)
                    if(len(admin_credential_ref) > 0):

                        if(key_2 != None and key_2.upper() == "PRIME"):
                            # hash - true
                            # user is admin - true
                            admin_credential_ref = admin_credential_ref[0]
                            if(admin_credential_ref.prime == True):
                                rdata = (True, int(data['data'])) # sending back hash related user data
                            else:
                                message = "ADMIN not PRIME."
                                logging.info("CHECK_TOKEN_ADMIN - {}".format(message))
                                rdata = (False, message)

                        else:
                            # hash - true
                            # user is admin - true
                            rdata = (True, int(data['data'])) # sending back hash related user data
                    
                    else:
                        message = "USER not ADMIN."
                        logging.info("CHECK_TOKEN_ADMIN - {}".format(message))
                        rdata = (False, message)
                
                else:
                    rdata = (False, "[1] Check key_1 sent to is_authorized()")
            
            else:
                rdata = (False, "[2] Check key_1 sent to is_authorized()")
        
        return rdata
    
    def sanction_authorization(self):
        import logging
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

        data = self.create_token()
        if(data['returned'] == False):
            logging.info("CREATE_TOKEN - {}".format(data['message']))
            rdata =  (False, data['message'])
        else:
            rdata = (True, data['data'])
        
        return rdata
    
    def revoke_authorization(self):
        import logging
        logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

        data = self.remove_token()
        if(data['returned'] == False):
            logging.info("REMOVE_TOKEN - {}".format(data['message']))
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

