from telegram.ext import *
from telegram import *

from hashlib import sha256
import sqlite3
from time import sleep
import sys
from datetime import (
        datetime,
        timedelta
    )
import os
from pathlib import Path
    
#-----------------------------


#-----------------------------

def create_password_hashed(password):
    sha256_ref = sha256()
    sha256_ref.update(f"ooga{password}booga".encode('utf-8'))
    return str(sha256_ref.digest())

cph = create_password_hashed

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

class TG_BOT(Bot):

    def __init__(self, api_key):
        super().__init__(api_key)
        self.API_KEY = api_key
        self.IN_TRANSIT = dict()

    def add_handlers(self):
        self.dispatcher.add_handler(CommandHandler('start', self.start_function))
        self.dispatcher.add_handler(CommandHandler('hello', self.start_function))
        self.dispatcher.add_handler(CommandHandler('logout', self.logout_function))
        self.dispatcher.add_handler(CommandHandler('login', self.login_function))
        self.dispatcher.add_handler(CommandHandler('email', self.email_function))
        self.dispatcher.add_handler(CommandHandler('pass', self.password_function))
    
    def send(self, chat_id, message, extras=None):
        if(extras == None):
            self.send_message(
                chat_id = chat_id,
                text = message,
                parse_mode = ParseMode.HTML
            )
        else:
            self.send_message(
                chat_id = chat_id,
                text = message,
                # parse_mode = ParseMode.HTML,
                reply_markup = extras
            )

    def logout_function(self, update, CallbackContext):
        try:
            query = r'''SELECT user_credential_id, user_profile_id_id FROM auth_prime_user_credential WHERE user_tg_id LIKE "{}";'''.format(update.effective_chat.id)
            self.connect()
            data = self.operation(query).fetchall()
            if(len(data) < 1):
                text = 'User Not Logged In !'
            else:
                query = r'''UPDATE auth_prime_user_credential SET user_tg_id = NULL WHERE user_credential_id = {};'''.format(int(data[0][0]))
                data = self.operation(query)
                text = f'''Successful.
                \nTelegram Account removed from profile.
                \nThank You, {update.effective_user.first_name} for using our Telegram Services.'''
                self.commit()
            self.disconnect()
        except Exception as ex:
            code = 'tg002'
            if(DEBUG == True):
                message = str(ex)
            else:
                message = "Contact Admin\t:\t@akash_sengupta_bsnl"
            text = f'''Unsuccessful.
            \nError Code\t:\t{code}
            \n{message}'''
        finally:
            self.send(update.effective_chat.id, text)
            print(f'[T] LOGOUT | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_user.first_name}')

    def start_function(self, update, CallbackContext):
        text = f'''Hi, {update.effective_user.first_name}
        \nCommand List :
        \n/start - Simple greeting
        \n/login - To initiate login
        \n/logout - To initiate logout'''
        print(f'[T] HELLO | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_user.first_name}')
        self.send(update.effective_chat.id, text)

    def login_function(self, update, CallbackContext):
        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.IN_TRANSIT[update.effective_chat.id] = dict()
        text = '''<b>/email</b> <i>email@domain.com</i>'''
        self.send(update.effective_chat.id, text)
        print(f'[T] LOGIN_1 | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_chat.id}')

    def email_function(self, update, CallbackContext):
        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.IN_TRANSIT[update.effective_chat.id] = dict()

        text = '''<b>/pass</b> <i>your_password</i>'''
        try:
            self.IN_TRANSIT[update.effective_chat.id]['email'] = update.message['text'].split()[1]
        except Exception:
            text = '''<b>/email</b> <i>email@domain.com</i>'''
        self.send(update.effective_chat.id, text)
        print(f'[T] LOGIN_2 | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_chat.id}')
    
    def password_function(self, update, CallbackContext):
        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.login_function(update, CallbackContext)
        try:
            self.IN_TRANSIT[update.effective_chat.id]['password'] = cph(update.message['text'].split()[1])
        except Exception:
            text = '''<b>/pass</b> <i>your_password</i>'''
        else:
            try:
                data = self.IN_TRANSIT[update.effective_chat.id]
                query = r'''SELECT user_credential_id, user_profile_id_id FROM auth_prime_user_credential WHERE user_email LIKE "{}" AND user_password LIKE "{}";'''.format(data['email'].lower(), data['password'])
                self.connect()
                data = self.operation(query).fetchall()
                if(len(data) < 1):
                    text = '<b>Invalid Credentials !</b>'
                else:
                    query = r'''UPDATE auth_prime_user_credential SET user_tg_id = "{}" WHERE user_credential_id = {};'''.format(update.effective_chat.id, int(data[0][0]))
                    data = self.operation(query)
                    text = '''Successful.
                    \nTelegram Account added to profile. 😀'''
                self.commit()
                self.disconnect()
            except Exception as ex:
                code = 'tg001'
                if(DEBUG == True):
                    message = str(ex)
                else:
                    message = "Contact Admin\t:\t@akash_sengupta_bsnl"
                text = f'Unsuccessful.\nError Code\t:\t{code}\nMessage\t:\t{message}'
            else:
                del(self.IN_TRANSIT[update.effective_chat.id])
            finally:
                self.send(update.effective_chat.id, text)
                print(f'[T] LOGIN_3 | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_chat.id}')

    def send_notifications(self, user_id, text):
        self.send(user_id, text)

    def run(self, key=None):
        try:
            self.get_me()
        except Exception:
            return False
        else:
            self.updater = Updater(token=self.API_KEY, use_context=True)
            self.dispatcher = self.updater.dispatcher
            self.add_handlers()
        
        if(key != None):
            try:
                self.updater.start_polling()
            except Exception:
                return False
        
        return True
