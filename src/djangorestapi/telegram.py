import traceback
import requests
import datetime
import logging
import re
import sqlite3
from hashlib import sha256

def create_hash(data):
    sha256_ref = sha256()
    sha256_ref.update(f"ooga{data}booga".encode('utf-8'))
    return str(sha256_ref.digest())

class BotHandler(object):
    
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

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

def main():
    logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

    token = "1470401355:AAErhMgyyWSAerh_JfN7BkdPwP37D1dl00U"
    db_url = 'test.sqlite3'

    JASS_EDUCATION = BotHandler(token)
    
    DB = Database(db_url)
    
    new_offset = 0
    print('***** TELEGRAM BACKEND ******')
    print('[.] Launching...')
    in_transit = list()

    while True:
        all_updates = JASS_EDUCATION.get_updates(new_offset)
        print(all_updates)

        if len(all_updates) > 0:
            for current_update in all_updates:
                first_update_id = current_update['update_id']

                if('edited_message' in current_update.keys()):
                    name = 'edited_message'
                elif('message' in current_update.keys()):
                    name = 'message'
                
                first_chat_text = current_update[f'{name}']['text']
                first_chat_id = current_update[f'{name}']['from']['id']
                first_chat_name = current_update[f'{name}']['from']['first_name']

                if first_chat_text == '/hello' or first_chat_text == '/start':
                    text = 'Hi, {}.'.format(first_chat_name)
                    text += '\n\nCommand List :\n/login - To initiate login\n/logout - To initiate logout.'
                    JASS_EDUCATION.send_message(first_chat_id, text)
                    new_offset = first_update_id + 1
                    logging.info('{} - {}:{}'.format(first_chat_text, first_chat_id, first_chat_name))
                elif first_chat_text == '/logout':
                    try:
                        query = r'''SELECT user_credential_id, user_profile_id_id FROM auth_prime_user_credential WHERE user_tg_id LIKE "{}";'''.format(first_chat_id)
                        DB.connect()
                        data = DB.operation(query)
                        data = data.fetchall()
                        if(len(data) < 1):
                            text = 'User Not Logged In !'
                        else:
                            query = r'''UPDATE auth_prime_user_credential SET user_tg_id = NULL WHERE user_credential_id = {};'''.format(int(data[0][0]))
                            data = DB.operation(query)
                            text = 'Successful.\nTelegram Account removed from profile.\nThank You, {} for using our Telegram Services.'.format(first_chat_name)
                            DB.commit()
                            DB.disconnect()
                    except Exception as ex:
                        traceback.print_exc()
                        code = 'tg002'
                        text = f'Unsuccessful.\nError Code : {code}\nContact Admin : @akash_sengupta_bsnl'

                    JASS_EDUCATION.send_message(first_chat_id, text)
                    new_offset = first_update_id + 1
                    logging.info('{} - {}:{}'.format(first_chat_text, first_chat_id, first_chat_name))
                else:
                    command = first_chat_text.split(' ')
                    if(len(command) == 2):
                        if(command[0] == '/login'):
                            PATTERN = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}:[a-zA-Z0-9~!@#$%^&*()_+]+$'
                            if(re.search(PATTERN, command[1])):
                                cred = command[1].split(':')
                                try:
                                    query = r'''SELECT user_credential_id, user_profile_id_id FROM auth_prime_user_credential WHERE user_email LIKE "{}" AND user_password LIKE "{}";'''.format(cred[0], create_hash(cred[1]))
                                    DB.connect()
                                    data = DB.operation(query)
                                    data = data.fetchall()
                                    if(len(data) < 1):
                                        text = 'Invalid Email or Password !'
                                    else:
                                        query = r'''UPDATE auth_prime_user_credential SET user_tg_id = "{}" WHERE user_credential_id = {};'''.format(first_chat_id, int(data[0][0]))
                                        data = DB.operation(query)
                                        text = 'Successful.\nTelegram Account added to profile.'
                                        DB.commit()
                                        DB.disconnect()

                                except Exception as ex:
                                    traceback.print_exc()
                                    code = 'tg001'
                                    text = f'Unsuccessful.\nError Code : {code}\nContact Admin : @akash_sengupta_bsnl'
                            else:
                                text = 'Invalid Formating.\nTry : /login email@domain.com:password'
                        else:
                            text = 'Invalid Formating.\nTry : /login email@domain.com:password'
                    else:
                        if(command[0] == '/login'):
                            text = 'Invalid Formating.\nTry : /login email@domain.com:password'
                        else:
                            text = 'Invalid Command.\nTry : /hello'
                    JASS_EDUCATION.send_message(first_chat_id, text)
                    new_offset = first_update_id + 1
                    logging.info('{} - {}:{}'.format(first_chat_text, first_chat_id, first_chat_name))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('[x] System Exit : KeyboardInterrupt.')
        print('Thank you for using JASS_TG_BOT_BACKEND.')
        exit(1)