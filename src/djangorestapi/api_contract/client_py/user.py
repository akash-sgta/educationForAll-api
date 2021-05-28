from client_py.jass_education import Jass_Education
import json


class User(Jass_Education):
    def __init__(self, api_key=None, base_url=None, uauth=None):
        super().__init__(api_key=api_key, url=base_url)
        self.__url = User.url_join(self.base_url, "api")
        self.__uauth = uauth

    @property
    def uauth(self):
        return self.__uauth

    @uauth.setter
    def uauth(self, data):
        self.__uauth = data

    @property
    def url(self):
        return self.__url

    # ----------------GET--------------------------------

    def getSpecificCred(self, pk=None, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=User.url_join(self.url, "user", "cred", f"{pk}"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text)["message"])
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def getSelfCred(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=User.url_join(self.url, "user", "cred", "0"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text)["message"])
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def getSpecificProfile(self, pk=None, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=User.url_join(self.url, "user", "profile", f"{pk}"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text)["message"])
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def getSelfProfile(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=User.url_join(self.url, "user", "prof", "0"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text)["message"])
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    # ----------------POST-------------------------------

    def signUp(self, data=None):
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            KEYS = ("first_name", "last_name", "email", "password")
            incoming_keys = data.keys()
            ret_data = (True, None)
            for key in KEYS:
                if key not in incoming_keys:
                    ret_data = (False, f"Key not provided => {key}")
                    break

            if ret_data[0]:
                try:
                    data = self.REQUEST.post(
                        url=User.url_join(self.url, "user", "cred"),
                        json={"action": "signup", "data": data},
                        headers={
                            "uauth": f"Token {None}",
                            "Authorization": f"Token {self.api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    if data.status_code // 100 != 2:
                        ret_data = (True, json.loads(data.text)["message"])
                    else:
                        ret_data = (True, data.json())
                except Exception as ex:
                    ret_data = (False, f"[EX] {ex}")

        return ret_data

    def signIn(self, data=None):
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            KEYS = ("email", "password")
            incoming_keys = data.keys()
            ret_data = (True, None)
            for key in KEYS:
                if key not in incoming_keys:
                    ret_data = (False, f"Key not provided => {key}")
                    break

            if ret_data[0]:
                try:
                    data = self.REQUEST.post(
                        url=User.url_join(self.url, "user", "cred"),
                        json={"action": "signin", "data": data},
                        headers={
                            "uauth": f"Token {None}",
                            "Authorization": f"Token {self.api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    if data.status_code // 100 != 2:
                        ret_data = (True, json.loads(data.text)["message"])
                    else:
                        ret_data = (True, data.json())
                except Exception as ex:
                    ret_data = (False, f"[EX] {ex}")

        return ret_data

    def forgotPassword(self, data=None):
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            KEYS = ["email"]
            incoming_keys = data.keys()
            ret_data = (True, None)
            for key in KEYS:
                if key not in incoming_keys:
                    ret_data = (False, f"Key not provided => {key}")
                    break

            if ret_data[0]:
                try:
                    data = self.REQUEST.post(
                        url=User.url_join(self.url, "user", "cred"),
                        json={"action": "forgotp", "data": data},
                        headers={
                            "uauth": f"Token {None}",
                            "Authorization": f"Token {self.api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    if data.status_code // 100 != 2:
                        ret_data = (True, json.loads(data.text)["message"])
                    else:
                        ret_data = (True, data.json())
                except Exception as ex:
                    ret_data = (False, f"[EX] {ex}")

        return ret_data

    def createProfile(self, uauth=None, data=None):
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            KEYS = ("headline", "bio")
            incoming_keys = data.keys()
            ret_data = (True, None)
            for key in KEYS:
                if key not in incoming_keys:
                    ret_data = (False, f"Key not provided => {key}")
                    break

            if ret_data[0]:
                try:
                    data = self.REQUEST.post(
                        url=User.url_join(self.url, "user", "prof"),
                        json=data,
                        headers={
                            "uauth": f"Token {None}",
                            "Authorization": f"Token {self.api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    if data.status_code // 100 != 2:
                        ret_data = (True, json.loads(data.text)["message"])
                    else:
                        ret_data = (True, data.json())
                except Exception as ex:
                    ret_data = (False, f"[EX] {ex}")

        return ret_data

    # ----------------PUT--------------------------------

    def editSelfCred(self, uauth=None, data=None):
        if uauth == None:
            uauth = self.uauth
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            KEYS = ("first_name", "last_name", "email")
            incoming_keys = data.keys()
            ret_data = (True, None)
            for key in KEYS:
                if key not in incoming_keys:
                    ret_data = (False, f"Key not provided => {key}")
                    break

            if ret_data[0]:
                try:
                    data = self.REQUEST.put(
                        url=User.url_join(self.url, "user", "cred", "0"),
                        json=data,
                        headers={
                            "uauth": f"Token {None}",
                            "Authorization": f"Token {self.api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    if data.status_code // 100 != 2:
                        ret_data = (True, json.loads(data.text)["message"])
                    else:
                        ret_data = (True, data.json())
                except Exception as ex:
                    ret_data = (False, f"[EX] {ex}")

        return ret_data

    def editSelfProfile(self, uauth=None, data=None):
        if uauth == None:
            uauth = self.uauth
        if data == None:
            ret_data = (False, "Data not filled")
        else:
            KEYS = ("headline", "bio")
            incoming_keys = data.keys()
            ret_data = (True, None)
            for key in KEYS:
                if key not in incoming_keys:
                    ret_data = (False, f"Key not provided => {key}")
                    break

            if ret_data[0]:
                try:
                    data = self.REQUEST.put(
                        url=User.url_join(self.url, "user", "prof", "0"),
                        json=data,
                        headers={
                            "uauth": f"Token {None}",
                            "Authorization": f"Token {self.api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    if data.status_code // 100 != 2:
                        ret_data = (True, json.loads(data.text)["message"])
                    else:
                        ret_data = (True, data.json())
                except Exception as ex:
                    ret_data = (False, f"[EX] {ex}")

        return ret_data

    # ----------------DELETE-----------------------------

    def deleteSelfCred(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=User.url_join(self.url, "user", "cred", "0"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text)["message"])
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def deleteSelfProfile(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=User.url_join(self.url, "user", "prof", "0"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text)["message"])
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def signOut(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=User.url_join(self.url, "user", "cred", "87795962440396049328460600526719"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text)["message"])
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data
