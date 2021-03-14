from development import *
from hashlib import sha256
import requests
import sqlite3
from time import sleep
import os
import platform
from pathlib import Path
import re
import threading
import sys
# -------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_URL = os.path.join(BASE_DIR, 'test.sqlite3')
STOP_PROC = False

# -------------------------------------------------------------------------
class BotHandler(object):
    
    def __init__(self, token=None):
        super().__init__()
        self._token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    @property
    def token(self):
        return self._token
    @token.setter
    def token(self, data):
        self._token = data
        self.api_url = "https://api.telegram.org/bot{}/".format(self.token)
    
    def get_updates(self, offset=0, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_first_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[0]
        else:
            last_update = None

        return last_update

class Database(object):

    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.conn = None
        self.cursor = None
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db)
        except Exception:
            return False
        else:
            return self.conn
    
    def disconnect(self):
        try:
            self.conn.close()
        except Exception:
            return False
        else:
            return True
    
    def commit(self):
        try:
            self.conn.commit()
        except Exception:
            return False
        else:
            return True

    def operation(self, query = None):
        if(query == None):
            return False
        else:
            self.cursor = self.conn.execute(query)
            return self.cursor
# -------------------------------------------------------------------------
