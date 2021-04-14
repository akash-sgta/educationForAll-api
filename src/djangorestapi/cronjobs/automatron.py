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
    
#-----------------------------

from config.cron_config import *

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

class TG_BOT(Bot, Database):

    def __init__(self, api_key, db_url):
        super().__init__(api_key)
        self.db = db_url
        self.IN_TRANSIT = dict()
        try:
            self.get_me()
        except Exception:
            print("[x] Network error")
        else:
            print("[T] Bot online..")
            self.updater = Updater(token=api_key, use_context=True)
            self.dispatcher = self.updater.dispatcher
            self.add_handlers()

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

    def run(self):
        try:
            self.updater.start_polling()
        except Exception:
            print("[x] Network error")

if __name__ == "__main__":
    bot = TG_BOT(TG_TOKEN, DB_URL)
    bot.run()

    while(True):
        try:
            # notification
            query = r'''SELECT user_credential_id_id, notification_id_id FROM user_personal_user_notification_int WHERE prime_1 = false;'''
            bot.connect()
            data = bot.operation(query).fetchall()
            if(len(data) < 1):
                print(f"[N] Notification count\t:\t0")
            else:
                print(f"[N] Notification count\t:\t{len(data)}")
                for notification in data:
                    query = r'''SELECT user_tg_id FROM auth_prime_user_credential WHERE user_credential_id = {};'''.format(notification[0])
                    user_tg_id_data = bot.operation(query).fetchall()
                    query = r'''SELECT notification_body, made_date FROM user_personal_notification WHERE notification_id = {};'''.format(notification[1])
                    notification_data = bot.operation(query).fetchall()
                    # print(user_tg_id_data, notification_data)
                    if(user_tg_id_data[0][0] not in (None, "")):
                        text = f"{notification_data[0][1]}\n{notification_data[0][0]}"
                        try:
                            bot.send(user_tg_id_data[0][0], text)
                        except:
                            print("EX : Network error")
                        else:
                            query = r'''UPDATE user_personal_user_notification_int SET prime_1 = True WHERE user_credential_id_id = {} and notification_id_id = {};'''.format(notification[0], notification[1])
                            data = bot.operation(query)
                    else:
                        print("[N] TG ID NOT FOUND")
            bot.commit()
            bot.disconnect()

            sleep(5)

            # token
            now = datetime.now()
            query = '''SELECT token_id, token_start FROM auth_prime_user_token_table LIMIT 10;'''
            bot.connect()
            data = bot.operation(query).fetchall()
            if(len(data) < 1):
                print('[t] Tokens Present\t:\t0')
            else:
                print(f'[t] Tokens Present\t:\t{len(data)}')
                text = list()
                for token_data in data:
                    token_id, token_end = int(token_data[0]), datetime.strptime(token_data[1].split()[0], '%Y-%m-%d')+timedelta(hours=48)
                    if(now > token_end):
                        text.append(token_id)
                        
                if(len(text) > 0):
                    query = '''DELETE FROM auth_prime_user_token_table WHERE token_id in ({});'''.format(",".join([str(x) for x in text]))
                    bot.operation(query)
                    print(f"[t] Overdue tokens cleared -> {text}")
                else:
                    print('[t] Tokens Overdue\t:\t0')

            bot.commit()
            bot.disconnect()
            
            sleep(5)
        except KeyboardInterrupt as ex:
            sys.exit('Keyboard Interrupt')
