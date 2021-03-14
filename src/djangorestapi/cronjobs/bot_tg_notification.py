from hashlib import sha256
import requests
import sqlite3
from time import sleep
import os
import platform
from pathlib import Path
import re

from development import *
from telegram_handler_bot import *

#----------------------------------------------------

class Notification_Handler(BotHandler, Database):

    def __init__(self, token, db):
        super().__init__()
        self.token = token
        self.db = db
    
    def run(self):
        try:
            while(True):
                query = r'''SELECT user_credential_id_id, notification_id_id FROM user_personal_user_notification_int WHERE prime_1 = false;'''
                self.connect()
                data = self.operation(query).fetchall()
                if(len(data) < 1):
                    pass

                else:
                    for notification in data:
                        query = r'''SELECT user_tg_id FROM auth_prime_user_credential WHERE user_credential_id = {};'''.format(notification[0])
                        user_tg_id_data = self.operation(query).fetchall()
                        query = r'''SELECT notification_body, made_date FROM user_personal_notification WHERE notification_id = {};'''.format(notification[1])
                        notification_data = self.operation(query).fetchall()
                        print(user_tg_id_data, notification_data)
                        text = f"{notification_data[0][1]}\n{notification_data[0][0]}"
                        self.send_message(user_tg_id_data[0][0], text)
                        query = r'''UPDATE user_personal_user_notification_int SET prime_1 = True WHERE user_credential_id_id = {} and notification_id_id = {};'''.format(notification[0], notification[1])
                        data = self.operation(query)

                self.commit()
                self.disconnect()

                sleep(5)

        except KeyboardInterrupt as ex:
            self.alive = False
            raise(KeyboardInterrupt)

# ------------------------------------------------------------------------

if __name__ == "__main__":

    try:
        if(platform.system().upper() == 'Windows'.upper()):
            os.system('cls')
        else:
            os.system('clear')
        print("\n\n*****************************************\n\n")
        print("[.] Starting telegram notification bot serivice...")
        bot = Notification_Handler(TG_TOKEN, DB_URL)
        bot.run()
    
    except KeyboardInterrupt:
        print("[!] Attempting to close service...")
        sleep(2)
        print("[!] Closing service.\n")
        print("[.] Thank You for using AUTOMATRON.\n")
        print("\n\n*****************************************\n\n")