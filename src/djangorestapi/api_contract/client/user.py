from client.jass_education import Jass_Education
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

    def get(self, uauth=None):
        headers = {
            "uauth": f"Token {uauth}",
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            data = self.REQUEST.get(url=self.uri, headers=headers)
            ret_data = (True, (data.status_code, data.json()))
        except:
            ret_data = (False, "Something went wrong. Try again later !")
        finally:
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

        if data == None:
            ret_data = (False, "Data not filled")
        else:
            flag = True
            sub_action = data["action"].lower()
            if sub_action == "signin" and not signin_check(data["data"])[0]:
                flag = False
            elif sub_action == "signup" and not signup_check(data["data"])[0]:
                flag = False

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
                        ret_data = self.get()
                    elif action.upper() == "POST":
                        ret_data = self.post(data=data, uauth=uauth)

        return ret_data
