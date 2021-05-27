import requests


class Jass_Education(object):
    def __init__(self, api_key=None, url=None):
        super().__init__()

        self.__api_key = None
        self.__url = None
        self.__request = requests.Session()
        self.__action = ("get", "post", "put", "delete", "options")

        if api_key != None:
            self.api_key = api_key
        if url != None:
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

    @action.setter
    def action(self, data):
        self.__action = data

    # ----------------------------------------------------

    def url_join(self, *args):
        return "/".join(args) + "/"

    def check_server(self):
        if (self.url == None) or (self.api_key == None):
            return (False, "[URL, API_KEY] required")
        else:
            try:
                data = self.REQUEST.get(url=self.url_join(self.url, "checkserver"))
            except Exception as ex:
                return (False, "Server unresponsive. Try again later !")
            else:
                return (True, (data.status_code, data.json()))
