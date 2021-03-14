from hashlib import sha256
import requests
import sqlite3
from time import sleep
import os
import platform
from pathlib import Path
import re
import datetime

from development import *
from telegram_handler_bot import *

#----------------------------------------------------
class Token_Handler(BotHandler, Database):

    def __init__(self, token, db):
        super().__init__()
        self.token = token
        self.db = db
    
    def run(self):
        try:
            while(True):
                now = datetime.now()
                query = '''SELECT token_id, token_end FROM auth_prime_user_token_table LIMIT 10;'''
                self.connect()
                data = self.operation(query).fetchall()
                if(len(data) < 1):
                    print('[.] No Tokens Present !')
                
                else:
                    text = list()
                    for token_data in data:
                        token_id, token_end = int(token_data[0]), datetime.strptime(token_data[1], '%d-%m-%Y %H:%M:%S')
                        if(now > token_end):
                            text.append(token_id)
                    
                    if(len(text) > 0):
                        query = '''DELETE FROM auth_prime_user_token_table WHERE token_id in ({});'''.format(",".join([str(x) for x in text]))
                        self.operation(query)
                        print(f"[.] Overdue tokens cleared -> {text}")
                    
                    else:
                        print('[.] No Tokens Overdue !')

                self.commit()
                self.disconnect()

                sleep(60*60)
        
        except KeyboardInterrupt as ex:
            self.alive = False
            raise(KeyboardInterrupt)

# -------------------------------------------------------------------------

if __name__ == "__main__":

    try:
        if(platform.system().upper() == 'Windows'.upper()):
            os.system('cls')
        else:
            os.system('clear')
        print("\n\n*****************************************\n\n")
        print("[.] Starting telegram token bot serivice...")
        bot = Token_Handler(TG_TOKEN, DB_URL)
        bot.run()
    
    except KeyboardInterrupt:
        print("[!] Attempting to close service...")
        sleep(2)
        print("[!] Closing service.\n")
        print("[.] Thank You for using AUTOMATRON.\n")
        print("\n\n*****************************************\n\n")