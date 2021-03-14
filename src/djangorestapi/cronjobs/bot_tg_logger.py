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

IN_TRANSIT = list()

class Telegram_Bot(BotHandler, Database):

    def __init__(self, token, db):
        super().__init__()
        self.token = token
        self.db = db
    
    def create_password_hashed(self, password=None):
        if(password == None):
            return False,"Initialize Password"
        else:
            from hashlib import sha256
            sha256_ref = sha256()
            sha256_ref.update(f"ooga{password}booga".encode('utf-8'))
            return str(sha256_ref.digest())

    def run(self):
        try:
            new_offset = 0
            while True:
                all_updates = self.get_updates(new_offset)
                print(f"[.] No of queries : {len(all_updates)}")
                if len(all_updates) > 0:
                    for current_update in all_updates:
                        try:
                            first_update_id = current_update['update_id']
                            if('edited_message' in current_update.keys()):
                                name = 'edited_message'

                            elif('message' in current_update.keys()):
                                name = 'message'
                            
                            first_chat_text = current_update[f'{name}']['text']
                            first_chat_id = current_update[f'{name}']['from']['id']
                            first_chat_name = current_update[f'{name}']['from']['first_name']

                            if(first_chat_text in ('/hello', '/start')):
                                text = 'Hi, {}.'.format(first_chat_name)
                                text += '\n\nCommand List :\n/hello - Simple greeting\n/login - To initiate login\n/logout - To initiate logout.'
                                self.send_message(first_chat_id, text)
                                new_offset = first_update_id + 1
                                print(f'[.] HELLO | ID : {first_chat_id} | NAME : {first_chat_name}')
                            
                            elif(first_chat_text == '/logout'):
                                try:
                                    query = r'''SELECT user_credential_id, user_profile_id_id FROM auth_prime_user_credential WHERE user_tg_id LIKE "{}";'''.format(first_chat_id)
                                    self.connect()
                                    data = self.operation(query).fetchall()
                                    if(len(data) < 1):
                                        text = 'User Not Logged In !'

                                    else:
                                        query = r'''UPDATE auth_prime_user_credential SET user_tg_id = NULL WHERE user_credential_id = {};'''.format(int(data[0][0]))
                                        data = self.operation(query)
                                        text = 'Successful.\nTelegram Account removed from profile.\nThank You, {} for using our Telegram Services.'.format(first_chat_name)
                                    
                                    self.commit()
                                    self.disconnect()
                                
                                except Exception as ex:
                                    code = 'tg002'
                                    if(DEBUG == True):
                                        message = str(ex)
                                    else:
                                        message = "Contact Admin : @akash_sengupta_bsnl"
                                    text = f'Unsuccessful.\nError Code : {code}\n{message}'
                                
                                else:
                                    self.send_message(first_chat_id, text)
                                    new_offset = first_update_id + 1
                                    print(f'[.] LOGOUT | ID : {first_chat_id} | NAME : {first_chat_name}')
                            
                            elif(first_chat_text == '/login'):
                                if(first_chat_id not in IN_TRANSIT):
                                    IN_TRANSIT.append(first_chat_id)
                                
                                text = 'Try : your_email:your_password'
                                self.send_message(first_chat_id, text)
                                new_offset = first_update_id + 1
                                print(f'[.] LOGIN_1 | ID : {first_chat_id} | NAME : {first_chat_name}')

                            else:
                                if(first_chat_id not in IN_TRANSIT):
                                    text = 'Invalid Command.\nTry : /hello'
                                    print(f'[.] OTHERS | ID : {first_chat_id} | NAME : {first_chat_name}')

                                else:
                                    PATTERN = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}:[a-zA-Z0-9~!@#$%^&*()_+]+$'
                                    if(re.search(PATTERN, first_chat_text)):
                                        email, password = first_chat_text.split(":")
                                        print(email, password, self.create_password_hashed(password))
                                        try:
                                            query = r'''SELECT user_credential_id, user_profile_id_id FROM auth_prime_user_credential WHERE user_email LIKE "{}" AND user_password LIKE "{}";'''.format(email.lower(), self.create_password_hashed(password))
                                            self.connect()
                                            data = self.operation(query).fetchall()
                                            if(len(data) < 1):
                                                text = 'Invalid Credentials !'

                                            else:
                                                query = r'''UPDATE auth_prime_user_credential SET user_tg_id = "{}" WHERE user_credential_id = {};'''.format(first_chat_id, int(data[0][0]))
                                                data = self.operation(query)
                                                text = 'Successful.\nTelegram Account added to profile. 😀'

                                            self.commit()
                                            self.disconnect()

                                        except Exception as ex:
                                            code = 'tg001'
                                            if(DEBUG == True):
                                                message = str(ex)
                                            else:
                                                message = "Contact Admin : @akash_sengupta_bsnl"
                                            text = f'Unsuccessful.\nError Code : {code}\nMessage : {message}'
                                        else:
                                            IN_TRANSIT.remove(first_chat_id)
                                    else:
                                        text = 'Invalid Formating.\nTry : your_email:your_password 😬'
                                    
                                    print(f'[.] LOGIN_2 | ID : {first_chat_id} | NAME : {first_chat_name}')

                                self.send_message(first_chat_id, text)
                                new_offset = first_update_id + 1
                        
                        except Exception as ex:
                            print(f'[x] Exception Occured : {str(ex)}')
                            new_offset = first_update_id + 1
                        else:
                            pass
        
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
        print("[.] Starting telegram logger bot serivice...")
        bot = Telegram_Bot(TG_TOKEN, DB_URL)
        bot.run()
    
    except KeyboardInterrupt:
        del(IN_TRANSIT)
        print("[!] Attempting to close service...")
        print("[!] Closing service.\n")
        print("[.] Thank You for using AUTOMATRON.\n")
        print("\n\n*****************************************\n\n")