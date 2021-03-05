import requests
from overrides import overrides
from overrides import final
import json
import random
from censusname import Censusname

class Jass_Education_Prime(object):

    def __init__(self, key=None, url=None, port=None):
        super().__init__()

        self.__api_key = None
        self.__url = None
        self.__port = None
        self.__api_version = "1.0"

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
                data = requests.get(url = self.url_join(self.url, 'checkserver'))
            except:
                return (False, "Server unresponsive. Try again later !")
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
                data = requests.get(url = url)
            except:
                return (False, "Something went wrong. Try again later !")
            else:
                return (True, (data.status_code, data.json()))
        
        def post():

            def signup(api = None):
                if(api == None):
                    return (False, "API credentials not filled")
                else:
                    if(data == None):
                        return (False, "Data not filled")
                    else:
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
                                    "action" : "signup",
                                    "data" : data
                                }
                            }
                            posting = json.dumps(posting)
                            post_data = requests.post(url = url, data = posting)
                        
                        except Exception as ex:
                            return (False, f"EX => {ex}")
                        
                        else:
                            return (True, (post_data.status_code, post_data.json()))

            # ----------------------------------------------------

            def signin(api = None):
                if(api == None):
                    return (False, "API credentials not filled")
                else:
                    if(data == None):
                        return (False, "Data not filled")
                    else:
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
                                    "action" : "signup",
                                    "data" : data
                                }
                            }
                            posting = json.dumps(posting)
                            post_data = requests.post(url = url, data = posting)
                        
                        except Exception as ex:
                            return (False, f"EX => {ex}")
                        
                        else:
                            return (True, (post_data.status_code, post_data.json()))

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
                else:
                    return (False, "Here")


        if(action not in self.action.keys()):
            return (False, "Invalid action")
        else:
            if(action.upper() == 'GET'):
                return get()
            elif(action.upper() == 'POST'):
                return post()
                

if __name__ == "__main__":

    JE = Jass_Education()
    JE.api_key = 'QRqWCH1NifWNVLcbcvpTBmVqve6gMlmWvhpsY0OPKBqbnYDXpvdDRLfRnzY1GYWj'
    JE.url = 'localhost'

    # checking if server is live
    data = JE.check_server()
    if((data[0] == True) and (data[1][0] == 200)):
        print(data[1][1])
    else:
        print(data[1])
    
    # action GET
    '''
    data = JE.user_credential_api(action = 'GET')
    if((data[0] == True) and (data[1][0] == 200)):
        for key, value in data[1][1].items():
            print(f"[GET] {key} => {value}")
    else:
        print(data[1])
    '''

    # action POST => signup
    '''
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
    if((data[0] == True) and (data[1][0] == 200)):
        for key, value in data[1][1].items():
            print(f"[POST] {key} => {value}")
    else:
        print(data[1])
    '''

    # action POST => signin
    temp = {
        "user_email" : f"email_{int(random.random()*100000 + 5)}@domain.com",
        "user_password" : "password_12345",
    }
    data = JE.user_credential_api(action = 'POST', action_sub = 'SIGNUP', data = temp)
    if((data[0] == True) and (data[1][0] == 200)):
        for key, value in data[1][1].items():
            print(f"[POST] {key} => {value}")
    else:
        print(data[1])


    

