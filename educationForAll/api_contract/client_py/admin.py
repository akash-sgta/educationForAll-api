from client_py.jass_education import Jass_Education
import json


class Admin(Jass_Education):
    def __init__(self, api_key=None, base_url=None, uauth=None):
        super().__init__(api_key=api_key, url=base_url)
        self.__url = Admin.url_join(self.base_url, "api")
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

    def getAllCred(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=Admin.url_join(self.url, "user", "cred", "87795962440396049328460600526719"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text))
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def getAllProfile(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=Admin.url_join(self.url, "user", "prof", "87795962440396049328460600526719"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text))
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    # ----------------POST-------------------------------

    # ----------------PUT--------------------------------

    # ----------------DELETE-----------------------------

    def deleteSpecificCred(self, pk=None, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=Admin.url_join(self.url, "user", "cred", f"{pk}"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text))
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def deleteAllCred(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=Admin.url_join(self.url, "user", "cred", "13416989436929794359012690353783"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text))
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def deleteSpecificProfile(self, pk=None, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=Admin.url_join(self.url, "user", "prof", f"{pk}"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text))
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data

    def deleteAllProfile(self, uauth=None):
        if uauth == None:
            uauth = self.uauth
        try:
            data = self.REQUEST.get(
                url=Admin.url_join(self.url, "user", "prof", "87795962440396049328460600526719"),
                headers={
                    "uauth": f"Token {uauth}",
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            if data.status_code // 100 == 2:
                ret_data = (True, data.json())
            else:
                ret_data = (True, json.loads(data.text))
        except Exception as ex:
            ret_data = (False, f"[EX] {ex}")

        return ret_data
