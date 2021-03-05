import requests
from overrides import overrides
from overrides import final
import json
import random
from censusname import Censusname
from os import system
import platform

class Jass_Education_Prime(object):

    def __init__(self, key=None, url=None, port=None):
        super().__init__()

        self.__api_key = None
        self.__url = None
        self.__port = None
        self.__api_version = "1.0"
        self.__request = requests.Session()

        if(key != None):
            self.api_key = key
        if(url != None):
            self.url = url
        if(port != None):
            self.port = port
    
    # ----------------------------------------------------

    @property
    def api_version(self):
        return self.__api_version

    @property
    def api_key(self):
        return self.__api_key
    @api_key.setter
    def api_key(self, data):
        self.__api_key = data
    
    @property
    def url(self):
        if(self.__port == None):
            return self.__url
        else:
            return f"{self.__url}:{self.__port}"
    @url.setter
    def url(self, data):
        self.__url = data
    
    @property
    def port(self):
        return None
    @port.setter
    def port(self, data):
        self.__port = data
    
    @property
    def REQUEST(self):
        return self.__request
    
    # ----------------------------------------------------

    @final
    def url_join(self, *args):
        url = "http://" + "/".join(args) + "/"
        return url
    
    @final
    def check_server(self):
        if((self.url == None) or (self.api_key == None)):
            return (False, "URL, API_KEY needed")
        else:
            try:
                data = self.REQUEST.get(url = self.url_join(self.url, 'checkserver'))
            except Exception as ex:
                return (False, f"Server unresponsive. Try again later !")
            else:
                return (True, (data.status_code, data.json()))
    
    # ----------------------------------------------------

    def user_credential_api(self, *args, **kwargs):
        return False
    
    def user_profile_api(self, *args, **kwargs):
        return False
    
    def admin_credential_api(self, *args, **kwargs):
        return False
    
    def admin_privilege_api(self, *args, **kwargs):
        return False
    
    def image_api(self, *args, **kwargs):
        return False
    
    # ----------------------------------------------------

class Jass_Education(Jass_Education_Prime):
    
    def __init__(self, key = None, url = None, port = None):
        super().__init__(key, url, port)
        self.__action = {
            'GET' : None,
            'POST' : ('SIGNUP', 'SIGNIN', 'LOGIN', 'SIGNOUT', 'LOGOUT', 'DELETE', 'EDIT', 'READ')
            }

    # ----------------------------------------------------

    @property
    def action(self):
        return self.__action

    # ----------------------------------------------------

    @overrides
    def user_credential_api(self, action = None, action_sub = None, data = None):

        url = self.url_join(self.url, 'api', 'user', 'user')

        def get():
            try:
                data = self.REQUEST.get(url = url)
            except:
                return (False, "Something went wrong. Try again later !")
            else:
                return (True, (data.status_code, data.json()))
        
        def post():

            # ----------------------------------------------------

            def signup(api = None):
                if(api == None):
                    return (False, "API credentials not filled")
                else:
                    if(data == None):
                        return (False, "Data not filled")
                    else:
                        ACTION = "signup"
                        KEYS = ("user_f_name", "user_m_name", "user_l_name", "user_email", "user_password", "user_security_question", "user_security_answer")
                        try:
                            incoming_keys = data.keys()
                            for key in KEYS:
                                if(key not in incoming_keys):
                                    return (False, f"Key not provided => {key}")
                                else:
                                    pass
                            
                            posting = {
                                "api" : api,
                                "data" : {
                                    "action" : ACTION,
                                    "data" : {
                                        "data" : data
                                    }
                                }
                            }
                            posting = json.dumps(posting)
                            post_data = self.REQUEST.post(url = url, data = posting)
                        
                        except Exception as ex:
                            return (False, f"EX => {ex}")
                        
                        else:
                            return (True, (post_data.status_code, post_data.json()))

            def signin(api = None):
                if(api == None):
                    return (False, "API credentials not filled")
                else:
                    if(data == None):
                        return (False, "Data not filled")
                    else:
                        ACTION = "signin"
                        KEYS = ("user_email", "user_password")
                        try:
                            incoming_keys = data.keys()
                            for key in KEYS:
                                if(key not in incoming_keys):
                                    return (False, f"Key not provided => {key}")
                                else:
                                    pass
                            
                            posting = {
                                "api" : api,
                                "data" : {
                                    "action" : ACTION,
                                    "data" : {
                                        "data" : data
                                        }
                                }
                            }
                            posting = json.dumps(posting)
                            post_data = self.REQUEST.post(url = url, data = posting)
                        
                        except Exception as ex:
                            return (False, f"EX => {ex}")
                        
                        else:
                            return (True, (post_data.status_code, post_data.json()))

            def signout(api = None):
                if(api == None):
                    return (False, "API credentials not filled")
                else:
                    if(data == None):
                        return (False, "Data not filled")
                    else:
                        ACTION = "signout"
                        KEYS = ("hash", "user_id")
                        try:
                            incoming_keys = data.keys()
                            for key in KEYS[:-1]:
                                if(key not in incoming_keys):
                                    return (False, f"Key not provided => {key}")
                                else:
                                    pass
                            
                            posting = {
                                "api" : api,
                                "data" : {
                                    "action" : ACTION,
                                    "data" : data
                                }
                            }
                            posting = json.dumps(posting)
                            post_data = self.REQUEST.post(url = url, data = posting)
                        
                        except Exception as ex:
                            return (False, f"EX => {ex}")
                        
                        else:
                            return (True, (post_data.status_code, post_data.json()))

            def delete(api = None):
                if(api == None):
                    return (False, "API credentials not filled")
                else:
                    if(data == None):
                        return (False, "Data not filled")
                    else:
                        ACTION = "delete"
                        KEYS = ("hash", "user_id")
                        try:
                            incoming_keys = data.keys()
                            for key in KEYS[:-1]:
                                if(key not in incoming_keys):
                                    return (False, f"Key not provided => {key}")
                                else:
                                    pass
                            
                            posting = {
                                "api" : api,
                                "data" : {
                                    "action" : ACTION,
                                    "data" : data
                                }
                            }
                            posting = json.dumps(posting)
                            post_data = self.REQUEST.post(url = url, data = posting)
                        
                        except Exception as ex:
                            return (False, f"EX => {ex}")
                        
                        else:
                            return (True, (post_data.status_code, post_data.json()))

            def edit(api = None):
                if(api == None):
                    return (False, "API credentials not filled")
                else:
                    if(data == None):
                        return (False, "Data not filled")
                    else:
                        ACTION = "edit"
                        KEYS = ("hash", "user_id")
                        try:
                            incoming_keys = data.keys()
                            for key in KEYS[:-1]:
                                if(key not in incoming_keys):
                                    return (False, f"Key not provided => {key}")
                                else:
                                    pass
                            
                            posting = {
                                "api" : api,
                                "data" : {
                                    "action" : ACTION,
                                    "data" : data
                                }
                            }
                            posting = json.dumps(posting)
                            post_data = self.REQUEST.post(url = url, data = posting)
                        
                        except Exception as ex:
                            return (False, f"EX => {ex}")
                        
                        else:
                            return (True, (post_data.status_code, post_data.json()))

            def read(api = None):
                if(api == None):
                    return (False, "API credentials not filled")
                else:
                    if(data == None):
                        return (False, "Data not filled")
                    else:
                        ACTION = "read"
                        KEYS = ("hash", "user_id")
                        try:
                            incoming_keys = data.keys()
                            for key in KEYS[:-1]:
                                if(key not in incoming_keys):
                                    return (False, f"Key not provided => {key}")
                                else:
                                    pass
                            
                            posting = {
                                "api" : api,
                                "data" : {
                                    "action" : ACTION,
                                    "data" : data
                                }
                            }
                            posting = json.dumps(posting)
                            post_data = self.REQUEST.post(url = url, data = posting)
                        
                        except Exception as ex:
                            return (False, f"EX => {ex}")
                        
                        else:
                            return (True, (post_data.status_code, post_data.json()))

            # ----------------------------------------------------

            if(action_sub not in self.action['POST']):
                return (False, "Invalid action_sub")
            else:
                api = {
                    "version" : self.api_version,
                    "auth" : self.api_key
                }
                if(action_sub.upper() == self.action['POST'][0]):
                    return signup(api = api)
                elif(action_sub.upper() in (self.action['POST'][1], self.action['POST'][2])):
                    return signin(api = api)
                elif(action_sub.upper() in (self.action['POST'][3], self.action['POST'][4])):
                    return signout(api = api)
                elif(action_sub.upper() == self.action['POST'][5]):
                    return delete(api = api)
                elif(action_sub.upper() == self.action['POST'][6]):
                    return edit(api = api)
                elif(action_sub.upper() == self.action['POST'][7]):
                    return read(api = api)
                else:
                    return (False, "Invalid action_sub")


        if(action not in self.action.keys()):
            return (False, "Invalid action")
        else:
            if(action.upper() == 'GET'):
                return get()
            elif(action.upper() == 'POST'):
                return post()
                

if __name__ == "__main__":

    if(platform.system().upper() == "WINDOWS"):
        system('cls')
    else:
        system('clear')

    JE = Jass_Education()
    JE.api_key = 'QRqWCH1NifWNVLcbcvpTBmVqve6gMlmWvhpsY0OPKBqbnYDXpvdDRLfRnzY1GYWj'
    JE.url = 'localhost'

    # checking if server is live
    data = JE.check_server()
    if((data[0] == True) and (data[1][0] == 200)):
        print(data[1][1])

        # action GET
        if(False):
            data = JE.user_credential_api(action = 'GET')

        # action POST => signup
        if(False):
            f_name = Censusname(nameformat='{given}')
            l_name = Censusname(nameformat='{surname}')

            temp = {
                "user_f_name" : f_name.generate(),
                "user_m_name" : random.choice((None, l_name.generate())),
                "user_l_name" : l_name.generate(),
                "user_email" : f"email_{int(random.random()*100000 + 5)}@domain.com",
                "user_password" : "password_12345",
                "user_security_question" : None,
                "user_security_answer" : None
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'SIGNUP', data = temp)

        # action POST => signin
        if(False):
            temp = {
                "user_email" : f"email_{random.choice((72171,39911))}@domain.com",
                "user_password" : "password_12345",
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'SIGNIN', data = temp)
        
        # action POST => signout as ADMIN
        if(False):
            HASH = "J8qnkUGRw0hTPPRUOO5o6j8bDCcuUVwORMwg5gg4F0fDjxzYqxduq4BCt0DMAbh3"
            temp = {
                "hash" : f"{HASH}",
                "user_id" : [2,2,2],
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'SIGNOUT', data = temp)

        # action POST => signout as USER
        if(False):
            HASH = "J8qnkUGRw0hTPPRUOO5o6j8bDCcuUVwORMwg5gg4F0fDjxzYqxduq4BCt0DMAbh3"
            temp = {
                "hash" : f"{HASH}",
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'SIGNOUT', data = temp)

        # action POST => delete as ADMIN
        if(False):
            HASH = "J8qnkUGRw0hTPPRUOO5o6j8bDCcuUVwORMwg5gg4F0fDjxzYqxduq4BCt0DMAbh3"
            temp = {
                "hash" : f"{HASH}",
                "user_id" : [2,2,2],
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'DELETE', data = temp)

        # action POST => delete as USER
        if(False):
            HASH = "1r6yvIj0QNX2lmM9yyVNpzThtCicTPvfxqFJI7KVWLQCsJa6Qx0SFpAKENlp2mzo"
            temp = {
                "hash" : f"{HASH}",
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'DELETE', data = temp)

        # action POST => edit
        if(False):
            f_name = Censusname(nameformat='{given}')
            l_name = Censusname(nameformat='{surname}')

            HASH = 'tJayfU218GEgal1M8E6sbluJwjCJbDRyBFdA6TTNUbvUMPFYZYKh4RwiPJOkivdL'
            temp = {
                "user_f_name" : f_name.generate(),
                "user_m_name" : random.choice((None, l_name.generate())),
                "user_l_name" : l_name.generate(),
                "user_email" : f"email_{random.choice((39911, 96681, 83791, int(random.random()*100000 + 5)))}@domain.com"
            }
            temp = {
                "hash" : HASH,
                "data" : temp
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'EDIT', data = temp)

        # action POST => read as ADMIN
        if(False):
            HASH = "lfHIqjemCK5PwkvxDHj4vQj1fiq5TfgtaaZ26GY4MSe7eWFGGiFRNTRgcV0kc5Tl"
            temp = {
                "hash" : f"{HASH}",
                "user_id" : ["a",2,28,2],
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'READ', data = temp)

        # action POST => READ as USER
        if(False):
            HASH = "lfHIqjemCK5PwkvxDHj4vQj1fiq5TfgtaaZ26GY4MSe7eWFGGiFRNTRgcV0kc5Tl"
            temp = {
                "hash" : f"{HASH}",
            }
            data = JE.user_credential_api(action = 'POST', action_sub = 'READ', data = temp)


        if(True):
            if((data[0] == True) and (data[1][0] == 200)):
                try:
                    for key, value in data[1][1].items():
                        print(f"[POST] {key} => {value}")
                except:
                    print(f"{data}")
            else:
                print(data[1])

    else:
        print(data[1])