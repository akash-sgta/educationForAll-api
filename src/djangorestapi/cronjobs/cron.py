from auth_prime.models import (
    User_Token_Table,
    User_Credential,
)

from user_personal.models import (
    User_Notification_Int,
)

from django.conf import settings

from hashlib import sha256
import os
from pathlib import Path
from datetime import datetime, timedelta

from telegram.ext import *
from telegram import *

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = os.path.join(BASE_DIR, 'log', 'cronlog.log')

# ---------------------------------------------------------

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
        now = datetime.now()
        log_data = list()

        try:
            user_cred_ref = User_Credential.objects.get(user_tg_id = update.effective_chat.id)
        except User_Credential.DoesNotExist:
            text = 'User Not Logged In !'
            # ----------
            log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGOUT - {update.effective_chat.id} - {text}")
        except Exception as ex:
            if(settings.DEBUG == True):
                text += f"\n{ex}"
            else:
                text = "Unsuccessful."
                text += "\nError At : <b>Logout</b>"
            # ----------
            log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [x] LOGOUT - {ex}")
        else:
            user_cred_ref.user_tg_id = None
            user_cred_ref.save()
            text = "Successful."
            text += "\nTelegram Account removed from profile."
            text += f"\nThank You, <b>{update.effective_user.first_name}</b> for using our Telegram Services."
            # ----------
            log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGOUT - {update.effective_chat.id} - Successful")
        finally:
            self.send(update.effective_chat.id, text)
            # ----------
            log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGOUT - {update.effective_chat.id}")
            log_data.append("\n")
            with open(FILE, 'a') as log_file:
                log_file.writelines(log_data)

    def start_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        text = f"Hi, {update.effective_user.first_name}"
        text += "\nCommand List :"
        text += "\n/start - Simple greeting"
        text += "\n/login - To initiate login"
        text += "\n/logout - To initiate logout"
        self.send(update.effective_chat.id, text)
        # ----------
        log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] HELLO - {update.effective_chat.id}")
        log_data.append("\n")
        with open(FILE, 'a') as log_file:
                log_file.writelines(log_data)

    def login_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.IN_TRANSIT[update.effective_chat.id] = dict()
        text = "<b>/email</b> <i>email@domain.com</i>"
        self.send(update.effective_chat.id, text)
        # ----------
        log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_L - {update.effective_chat.id}")
        log_data.append("\n")
        with open(FILE, 'a') as log_file:
            log_file.writelines(log_data)

    def email_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        # in case login command was not used
        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.IN_TRANSIT[update.effective_chat.id] = dict()
        try:
            self.IN_TRANSIT[update.effective_chat.id]['email'] = update.message['text'].split()[1]
        except Exception as ex:
            text = "<b>/email</b> <i>email@domain.com</i>"
            # ----------
            log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [x] LOGIN_E - {ex}")
        else:
            text = "<b>/pass</b> <i>your_password</i>"
        self.send(update.effective_chat.id, text)
        # ----------
        log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_E - {update.effective_chat.id}")
        log_data.append("\n")
        with open(FILE, 'a') as log_file:
                log_file.writelines(log_data)
    
    def password_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        if(update.effective_chat.id not in self.IN_TRANSIT):
            self.login_function(update, CallbackContext) # if login or email none was initialized
        else:
            try:
                self.IN_TRANSIT[update.effective_chat.id]['password'] = self.create_password_hashed(update.message['text'].split()[1])
            except Exception as ex:
                text = '''<b>/pass</b> <i>your_password</i>'''
                # ----------
                log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [x] LOGIN_P - {ex}")
            else:
                data = self.IN_TRANSIT[update.effective_chat.id]
                try:
                    user_cred_ref = User_Credential.objects.get(user_email = data['email'].lower(), user_password = data['password'])
                except User_Credential.DoesNotExist:
                    text = "<b>Invalid Credentials !</b>"
                    # ----------
                    log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_P - Unsucessful")
                except Exception as ex:
                    if(settings.DEBUG == True):
                        text += f"\n{ex}"
                    else:
                        text = "Unsuccessful."
                        text += "\nError At : <b>Login_P</b>"
                    # ----------
                    log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [x] LOGIN_P - {ex}")
                else:
                    user_cred_ref.user_tg_id = update.effective_chat.id
                    user_cred_ref.save()
                    del(self.IN_TRANSIT[update.effective_chat.id])
                    text = "Successful."
                    text += "\nTelegram Account added to profile. 😀"
                    # ----------
                    log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_P - Sucessful")
            finally:
                self.send(update.effective_chat.id, text)
                # ----------
                log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_P - {update.effective_chat.id}")
                log_data.append("\n")
                with open(FILE, 'a') as log_file:
                    log_file.writelines(log_data)

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

# ---------------------------------------------------------

def telegram_notification():
    print("---------------------------")
    print("TELEGRAM_NOTIFICATION")
    log_data = list()
    now = datetime.now()

    with open(os.path.join(BASE_DIR, 'config', 'keys', 'TG_KEY.txt'), 'r') as secret:
        TG_TOKEN = secret.read().strip()[:-2]

    bot = TG_BOT(api_key=TG_TOKEN)
    if(bot.run()):
        notifications = User_Notification_Int.objects.filter(prime_1 = False)[:50]
        count = 0
        for notif in notifications:
            tg_id = notif.user_credential_id.user_tg_id
            if(tg_id == None):
                notif.tries += 1
                notif.save()
            else:
                notif_main = notif.notification_id.notification_body
                bot.send_notifications(tg_id, notif_main)
                notif.prime_1 = True
                notif.save()
                count += 1
        log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: NOTIFICATION CRONJOB\t\t:: [.] Notification Sent {count}")

    else:
        log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: NOTIFICATION CRONJOB\t\t:: [*] Notification - Could Not Start")
    
    log_data.append("\n")
    with open(FILE, 'a') as log_file:
        log_file.writelines(log_data)

def token_checker():
    print("---------------------------")
    print("TOKEN_CHECKER")
    log_data = list()
    now = datetime.now()

    token_ref = User_Token_Table.objects.all().order_by('token_id')[:10]
    token_delete_count = 0
    for token in token_ref:
        then = datetime.strptime(str(token.token_start).split(".")[0], "%Y-%m-%d %H:%M:%S") + timedelta(hours=48)
        if(then < now):
            token.delete()
            token_delete_count += 1
    log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TOKEN CRONJOB\t\t:: [.] Tokens expired : {token_delete_count}")
    log_data.append("\n")
    with open(FILE, 'a') as log_file:
        log_file.writelines(log_data)

def telegram_bot():
    print("---------------------------")
    print("TELEGRAM_BOT")
    now = datetime.now()
    log_data = list()

    with open(os.path.join(BASE_DIR, 'config', 'keys', 'TG_KEY.txt'), 'r') as secret:
        TG_TOKEN = secret.read().strip()[:-2]

    bot = TG_BOT(api_key=TG_TOKEN)
    if(bot.run()):
        try:
            # ----------
            log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [*] POLLING - Started..")
            
            bot.run('START_POLLING')
        except Exception as ex:
            # ----------
            log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [*] POLLING - {ex}")
    else:
        log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [*] POLLING - Could Not Start")
    
    log_data.append("\n")
    with open(FILE, 'a') as log_file:
        log_file.writelines(log_data)

def test():
    print("---------------------------")
    print("TEST")
    now = datetime.now()
    log_data = list()
    
    log_data.append(f"{now.strftime('%Y-%m-%d %H:%M:%S')} :: TEST CRONJOB\t\t:: [*] POPPED")
    log_data.append("\n")
    with open(FILE, 'a') as log_file:
        log_file.writelines(log_data)
