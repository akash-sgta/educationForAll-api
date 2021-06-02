import threading

from analytics.models import Log
from auth_prime.models import Api_Token


class Logger(threading.Thread):
    def __init__(self, api_id):
        super().__init__()
        self.__api_id = api_id
        self.__action = None

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, data):
        if type(data) == type(list()) or type(data) == type(tuple()):
            self.__action = data
        else:
            raise Exception("Invalid data type : List or Tuple supported")

    def run(self):
        try:
            Log(body=self.action, api_token_ref=Api_Token.objects.get(pk=self.action)).save()
        except Api_Token.DoesNotExist:
            pass
