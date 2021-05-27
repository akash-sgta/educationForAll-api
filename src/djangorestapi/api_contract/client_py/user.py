from client_py.jass_education import Jass_Education
import json


class User(Jass_Education):
    def __init__(self, api_key=None, url=None):
        super().__init__(api_key=api_key, url=url)
        self.uri = self.url_join(self.url, "api", "user", "cred")
        self.action = self.REQUEST.options(
            url=self.uri,
            headers={
                "uauth": f"Token {None}",
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            },
        ).json()["Allow"]

    def get(self, data=None, uauth=None):
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            headers = {
                "uauth": f"Token {uauth}",
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            }
            target = data["target"].lower()
            if target == "self":
                pk = "0"
            elif target == "all":
                pk = "87795962440396049328460600526719"
            else:
                pk = target
            try:
                data = self.REQUEST.get(url=self.uri + pk, headers=headers)
                ret_data = (True, (data.status_code, data.json()))
            except:
                ret_data = (False, "Something went wrong. Try again later !")

        return ret_data

    def post(self, data=None, uauth=None):
        def signup_check(data):
            KEYS = ("first_name", "last_name", "email", "password")
            incoming_keys = data.keys()
            ret_data = (True, None)
            for key in KEYS:
                if key not in incoming_keys:
                    ret_data = (False, f"Key not provided => {key}")
                    break
            return ret_data

        def signin_check(data):
            KEYS = ("email", "password")
            incoming_keys = data.keys()
            ret_data = (True, None)
            for key in KEYS:
                if key not in incoming_keys:
                    ret_data = (False, f"Key not provided => {key}")
                    break
            return ret_data

        def forgotp_check(data):
            if "email" not in data.keys():
                ret_data = (False, f"Key not provided => email")
            else:
                ret_data = (True, None)
            return ret_data

        if data == None:
            ret_data = (False, "Data not filled")
        else:
            flag = False
            sub_action = data["action"].lower()
            if sub_action == "signin" and signin_check(data["data"])[0]:
                flag = True
            elif sub_action == "signup" and signup_check(data["data"])[0]:
                flag = True
            elif sub_action == "forgotp" and forgotp_check(data["data"])[0]:
                flag = True

            if flag:
                headers = {
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                }
                try:
                    response = self.REQUEST.post(self.uri, json=data, headers=headers)
                    if response.status_code // 100 != 2:
                        ret_data = (True, (response.status_code, json.loads(response.text)["message"]))
                    else:
                        ret_data = (True, (response.status_code, response.json()["data"]))
                except Exception as ex:
                    ret_data = (False, f"[EX] {ex}")
            else:
                ret_data = (False, "Serialising error, check KEYS")
        return ret_data

    def put(self, data=None, uauth=None):
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            flag = False
            headers = {
                "uauth": f"Token {uauth}",
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            }
            target = data["target"].lower()
            if target == "self":
                pk = "0"
            try:
                response = self.REQUEST.put(self.uri + "0", json=data, headers=headers)
                if response.status_code // 100 != 2:
                    ret_data = (True, (response.status_code, json.loads(response.text)["message"]))
                else:
                    ret_data = (True, (response.status_code, response.json()["data"]))
            except Exception as ex:
                ret_data = (False, f"[EX] {ex}")
        return ret_data

    def delete(self, data=None, uauth=None):
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            headers = {
                "uauth": f"Token {uauth}",
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            }
            target = data["target"].lower()
            if target == "self":
                pk = "0"
            elif target == "all":
                pk = "13416989436929794359012690353783"
            elif target == "signout":
                pk = "87795962440396049328460600526719"
            else:
                pk = target
            try:
                data = self.REQUEST.get(url=self.uri + pk, headers=headers)
                ret_data = (True, (data.status_code, data.json()))
            except:
                ret_data = (False, "Something went wrong. Try again later !")

        return ret_data

    def run(self, action=None, data=None, uauth=None):
        if self.api_key == None:
            ret_data = (False, "API credentials not filled")
        else:
            if action == None:
                ret_data = (False, "Action : None, Not applicable")
            else:
                if action.upper() not in self.action:
                    ret_data = (False, f"Invalid Action : {action}, options : {self.action}")
                else:
                    if action.upper() == "GET":
                        ret_data = self.get(data=data, uauth=uauth)
                    elif action.upper() == "POST":
                        ret_data = self.post(data=data, uauth=uauth)
                    elif action.upper() == "PUT":
                        ret_data = self.put(data=data, uauth=uauth)
                    elif action.upper() == "DELETE":
                        ret_data = self.delete(data=data, uauth=uauth)
                    else:
                        ret_data = (False, "Invalid Action.")

        return ret_data
