import requests
import json


class Jass_Education(object):
    def __init__(self, api_key=None, base_url=None):
        super().__init__()

        self.__api_key = api_key
        self.__base_url = base_url
        self.__request = requests.Session()
        self.__action = "GET POST PUT DELETE OPTIONS".split()

    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, data):
        self.__api_key = data

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, data):
        self.__base_url = data

    @property
    def REQUEST(self):
        return self.__request

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, data):
        self.__action = data

    @staticmethod
    def url_join(*args):
        return "/".join(args)

    def check_server(self):
        if (self.base_url == None) or (self.api_key == None):
            ret_data = (False, "[URL, API_KEY] required")
        else:
            try:
                data = self.REQUEST.get(url=self.url_join(self.base_url, "checkserver"))
                if data.status_code // 100 == 2:
                    ret_data = (True, data.json())
                else:
                    ret_data = (True, json.loads(data.text)["message"])
            except Exception as ex:
                return (False, None)
