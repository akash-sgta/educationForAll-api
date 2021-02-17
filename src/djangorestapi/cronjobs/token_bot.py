from development import *
import sqlite3
from time import sleep
from datetime import datetime
import os
import platform
from pathlib import Path
# -------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_URL = os.path.join(BASE_DIR, 'test.sqlite3')
STOP_PROC = False
IN_TRANSIT = list()
# -------------------------------------------------------------------------
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
def token_bot():

    while(True):
    
        now = datetime.now()

        db_url = DB_URL
        DB = Database(db_url)

        query = '''SELECT token_id, token_end FROM auth_prime_token_table LIMIT 10;'''
        DB.connect()
        
        data = DB.operation(query)
        data = data.fetchall()

        if(len(data) < 1):
            print('[.] No Tokens Present !')
        else:
            text = list()
            for token_data in data:
                token_id, token_end = int(token_data[0]), datetime.strptime(token_data[1], '%d-%m-%Y %H:%M:%S')
                if(now > token_end):
                    text.append(token_id)
            if(len(text) > 0):

                query = '''DELETE FROM auth_prime_token_table WHERE token_id in ({});'''.format(",".join([str(x) for x in text]))
                
                DB.operation(query)
                print(f"[.] Overdue tokens cleared -> {text}")
            else:
                print('[.] No Tokens Overdue !')

        DB.commit()
        DB.disconnect()

        sleep(3600)
# -------------------------------------------------------------------------
if __name__ == "__main__":

    try:
        if(platform.system().upper() == 'Windows'.upper()):
            os.system('cls')
        else:
            os.system('clear')
        print("\n\n*****************************************\n\n")
        print("[.] Starting telegram bot serivice...")
        token_bot()
    
    except KeyboardInterrupt:
        del(IN_TRANSIT)
        print("[!] Attempting to close service...")
        sleep(2)
        print("[!] Closing service.\n")
        print("[.] Thank You for using AUTOMATRON.\n")
        print("\n\n*****************************************\n\n")