import requests
import json
import random
import os
import platform
from pathlib import Path

class Jass_Education(object):
    
    def __init__(self, api_key = None, url = None, port = None):
        super().__init__()

        self.__api_key = None
        self.__url = None
        self.__request = requests.Session()
        self.__action = ('get', 'post', 'put', 'delete')

        if(api_key != None):
            self.api_key = api_key
        if(url != None):
            self.url = url

    # ----------------------------------------------------

    @property
    def api_key(self):
        return self.__api_key
    @api_key.setter
    def api_key(self, data):
        self.__api_key = data
    
    @property
    def url(self):
        return self.__url
    @url.setter
    def url(self, data):
        self.__url = data
    
    @property
    def REQUEST(self):
        return self.__request
    
    @property
    def action(self):
        return self.__action
    
    # ----------------------------------------------------

    def url_join(self, *args):
        return "http://" + "/".join(args) + "/"
    
    def check_server(self):
        if((self.url == None) or (self.api_key == None)):
            return (False, "[URL, API_KEY] required")
        else:
            try:
                data = self.REQUEST.get(url = self.url_join(self.url, 'checkserver'))
            except Exception as ex:
                return (False, "Server unresponsive. Try again later !")
            else:
                return (True, (data.status_code, data.json()))

    # ----------------------------------------------------

    def user_credential_api(self, action = None, user_key = None, data = None):

        url = self.url_join(self.url, 'api', 'user', 'cred')
        headers = dict()
        
        def get():
            try:
                data = self.REQUEST.get(url = url)
            except:
                return (False, "Something went wrong. Try again later !")
            else:
                return (True, (data.status_code, data.json()))
        
        def post(data = None):
            
            # ----------------------------------------------------

            def signup_check(data = None):
                if(data == None):
                    return (False, "Data not filled")
                else:
                    KEYS = ("user_f_name", "user_l_name", "user_email", "user_password")
                    incoming_keys = data.keys()
                    for key in KEYS:
                        if(key not in incoming_keys):
                            return (False, f"Key not provided => {key}")
                    
                    return (True, 0)

            def signin_check(data = None):
                if(data == None):
                    return (False, "Data not filled")
                else:
                    KEYS = ("user_email", "user_password")
                    incoming_keys = data.keys()
                    for key in KEYS:
                        if(key not in incoming_keys):
                            return (False, f"Key not provided => {key}")
                    
                    return (True, 0)

            # ----------------------------------------------------

            if(data == None):
                return (False, "Data not filled")
            else:
                flag = True
                sub_action = data['action'].lower()
                if(sub_action == 'signup'):
                    check = signin_check(data['data'])
                    if(check[0] == False):
                        print(f"[x] {check[1]}")
                        flag = False
                    else:
                        flag = True
                
                if(flag):
                    headers['uauth'] = f"Token {None}"
                    try:
                        print(headers)
                        print(data)
                        response = self.REQUEST.post(url, data=data, headers = headers)
                        print(response.json())
                    except Exception as ex:
                        print(f"[x] {ex}")

            
        if(self.api_key == None):
            return (False, "API credentials not filled")
        if(action.lower() not in self.action):
            return (False, "Invalid action")
        else:
            headers["Authorization"] = f"Token {self.api_key}"
            headers["content-type"] = "application/json"
            if(action.upper() == 'GET'):
                return get()
            elif(action.upper() == 'POST'):
                return post(data = data)

if __name__ == "__main__":

    if(platform.system().upper() == "WINDOWS"):
        os.system('cls')
    else:
        os.system('clear')

    service = Jass_Education(api_key = '5Xw78vKVSwY6mahmTrUDGJPMvLam7zGFmRY7TDAyiXRR3TZCOsL8Yd5A0riLQYmp', url='localhost:8000')
    
    # checking if server is live
    data = service.check_server()
    if((data[0] == True) and (data[1][0] == 200)):
        print(data[1][1])

        BASE_DIR = Path(__file__).resolve().parent
        #------------------------UserCredential---------------------------------------

        # action POST => signup
        if(True):
            file_name = os.path.join(BASE_DIR, 'json', 'user_credential.json')
            with open(file_name, 'r') as json_file:
                temp = json.load(json_file)
            # user dependent code
            temp = temp['list_of_actions'][0]['input']
            data = service.user_credential_api(action = 'POST', user_key = None, data = temp)

    else:
        print(data[1])