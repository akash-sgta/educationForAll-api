from telegram.ext import *
from telegram import *

from pathlib import Path
import os
from hashlib import sha256
from time import sleep

from database_sql import Database

# ---------------------------------

class TG_BOT(Bot, Database):

    def __init__(self, api_key):
        super().__init__(api_key)
        self.API_KEY = api_key
        
        #-----------------------------------------------------------------------
        BASE = Path(__file__).resolve().parent.parent
        self.LOG_PATH = os.path.join(BASE, 'log', 'bot_telegram.log')

        with open(os.path.join(BASE, 'config', 'debug.txt'), 'r') as debug_status:
            DEBUG = debug_status.read()[1:-1]
            if(DEBUG == 'True'):
                self.DEBUG = True
            else:
                self.DEBUG = False
        if(self.DEBUG):
            self.type = 'sqlite'
            self.data = {
                "database" : os.path.join(BASE, 'test_databases', 'app.db.sqlite3')
            }
        else:
            self.type = 'mysql'
            self.data = {
                'database':  "appDB",
                'user': "admin",
                'password': "GANDUgandu",
                'host': "projectdatabase1.czbsimzcrcxe.ap-south-1.rds.amazonaws.com",
                'port' : "6969"
            }

        #-----------------------------------------------------------------------

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
            self.connect()
            returnData = self.select_sql(
                appName = 'auth_prime',
                tableName = 'user_credential',
                columnName = ['user_credential_id'],
                condition = f'''user_tg_id LIKE {update.effective_chat.id}'''
            )
            self.disconnect()
            if(len(returnData) < 1):
                text = 'User Not Logged In !'
            else:
                self.connect()
                data = self.update_sql(
                    appName = 'auth_prime',
                    tableName = 'user_credential',
                    columnChanges = 'user_tg_id = NULL',
                    condition = f'''user_credential_id = {returnData[0][0]}'''
                )
                self.commit()
                self.disconnect()
                text = f'''Successful.
                \nTelegram Account removed from profile.
                \nThank You, <b>{update.effective_user.first_name}</b> for using our Telegram Services.'''
                self.commit()
            self.disconnect()
        except Exception as ex:
            code = 'tg002'
            if(self.DEBUG == True):
                message = str(ex)
            else:
                message = "Contact Admin\t:\t@akash_sengupta_bsnl"
            text = f'''Unsuccessful.
            \nError Code\t:\t{code}
            \n{message}'''
        finally:
            self.send(update.effective_chat.id, text)
            with open(self.LOG_PATH, 'a') as log:
                log.write(f'[T] LOGOUT | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_user.first_name}\n')

    def start_function(self, update, CallbackContext):
        text = f'''Hi, {update.effective_user.first_name}
        \nCommand List :
        \n/start - Simple greeting
        \n/login - To initiate login
        \n/logout - To initiate logout'''
        with open(self.LOG_PATH, 'a') as log:
            log.write(f'[T] HELLO | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_user.first_name}\n')
        self.send(update.effective_chat.id, text)

    def login_function(self, update, CallbackContext):
        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.IN_TRANSIT[update.effective_chat.id] = dict()
        text = '''<b>/email</b> <i>email@domain.com</i>'''
        self.send(update.effective_chat.id, text)
        with open(self.LOG_PATH, 'a') as log:
            log.write(f'[T] LOGIN_1 | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_chat.id}\n')

    def email_function(self, update, CallbackContext):
        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.IN_TRANSIT[update.effective_chat.id] = dict()

        text = '''<b>/pass</b> <i>your_password</i>'''
        try:
            self.IN_TRANSIT[update.effective_chat.id]['email'] = update.message['text'].split()[1]
        except Exception:
            text = '''<b>/email</b> <i>email@domain.com</i>'''
        self.send(update.effective_chat.id, text)
        with open(self.LOG_PATH, 'a') as log:
            log.write(f'[T] LOGIN_2 | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_chat.id}\n')
    
    def password_function(self, update, CallbackContext):
        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.login_function(update, CallbackContext)
        try:
            self.IN_TRANSIT[update.effective_chat.id]['password'] = self.create_password_hashed(update.message['text'].split()[1])
        except Exception:
            text = '''<b>/pass</b> <i>your_password</i>'''
        else:
            try:
                data = self.IN_TRANSIT[update.effective_chat.id]
                
                self.connect()
                returnData = self.select_sql(
                    appName = 'auth_prime',
                    tableName = 'user_credential',
                    columnName = ['user_credential_id'],
                    condition = f'''user_email LIKE "{data['email'].lower()}" AND user_password LIKE "{data['password']}"'''
                )
                self.disconnect()
                
                if(len(data) < 1):
                    text = '<b>Invalid Credentials !</b>'
                else:
                    self.connect()
                    data = self.update_sql(
                        appName = 'auth_prime',
                        tableName = 'user_credential',
                        columnChanges = f'''user_tg_id = {update.effective_chat.id}''',
                        condition = f'''user_credential_id = {returnData[0][0]}'''
                    )
                    self.commit()
                    self.disconnect()
                    text = '''Successful.
                    \nTelegram Account added to profile. 😀'''
            except Exception as ex:
                code = 'tg001'
                if(self.DEBUG == True):
                    message = str(ex)
                else:
                    message = "Contact Admin\t:\t@akash_sengupta_bsnl"
                text = f'Unsuccessful.\nError Code\t:\t{code}\nMessage\t:\t{message}'
            else:
                del(self.IN_TRANSIT[update.effective_chat.id])
            finally:
                self.send(update.effective_chat.id, text)
                with open(self.LOG_PATH, 'a') as log:
                    log.write(f'[T] LOGIN_3 | ID\t:\t{update.effective_chat.id} | NAME\t:\t{update.effective_chat.id}\n')

    def send_notifications(self, user_id, text):
        self.send(user_id, text)
    
    def create_password_hashed(self, password):
        sha256_ref = sha256()
        sha256_ref.update(f"ooga{password}booga".encode('utf-8'))
        return str(sha256_ref.digest())

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

def main():
    BASE_DIR = Path(__file__).resolve().parent.parent
    with open(os.path.join(BASE_DIR, 'config', 'ambiguous', 'TG_KEY.txt'), 'r') as secret:
        TG_TOKEN = secret.read().strip()[:-2]
    bot = TG_BOT(api_key=TG_TOKEN)
    if(bot.run() == True):
        print("Bot started polling data from server ...")
        try:
            bot.run('START_POLLING')
        except KeyboardInterrupt:
            with open(bot.LOG_PATH, 'a') as log:
                log.write("="*25, "\n")

# main()