from telegram.ext import *
from telegram import *

import os
from pathlib import Path
from datetime import datetime
from hashlib import sha256

from auth_prime.models import (
    User,
)

from django.conf import settings

# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = os.path.join(BASE_DIR, "log", "cronlog.log")


class TG_BOT(Bot):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.API_KEY = api_key
        self.IN_TRANSIT = dict()

    def add_handlers(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start_function))
        self.dispatcher.add_handler(CommandHandler("hello", self.start_function))
        self.dispatcher.add_handler(CommandHandler("logout", self.logout_function))
        self.dispatcher.add_handler(CommandHandler("login", self.login_function))
        self.dispatcher.add_handler(CommandHandler("email", self.email_function))
        self.dispatcher.add_handler(CommandHandler("pass", self.password_function))

    def send(self, chat_id, message, extras=None):
        if extras == None:
            self.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
        else:
            self.send_message(
                chat_id=chat_id,
                text=message,
                # parse_mode = ParseMode.HTML,
                reply_markup=extras,
            )

    def logout_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        try:
            user_cred_ref = User.objects.get(telegram_id=update.effective_chat.id)
        except User.DoesNotExist:
            text = "User Not Logged In !"
            # ----------
            log_data.append(
                f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGOUT - {update.effective_chat.id} - {text}"
            )
        except Exception as ex:
            if settings.DEBUG == True:
                text += f"\n{ex}"
            else:
                text = "Unsuccessful."
                text += "\nError At : <b>Logout</b>"
            # ----------
            log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [x] LOGOUT - {ex}")
        else:
            user_cred_ref.telegram_id = None
            user_cred_ref.save()
            text = "Successful."
            text += "\nTelegram Account removed from profile."
            text += f"\nThank You, <b>{update.effective_user.first_name}</b> for using our Telegram Services."
            # ----------
            log_data.append(
                f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGOUT - {update.effective_chat.id} - Successful"
            )
        finally:
            self.send(update.effective_chat.id, text)
            # ----------
            log_data.append(
                f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGOUT - {update.effective_chat.id}"
            )
            with open(FILE, "a") as log_file:
                log_file.writelines(log_data)

    def start_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        text = f"Hi, {update.effective_user.first_name}"
        text += "\nCommand List :"
        text += "\n/hello - Simple greeting"
        if len(User.objects.filter(telegram_id=update.effective_chat.id)) < 1:
            text += "\n/login - To initiate login"
        else:
            text += "\n/logout - To initiate logout"
        self.send(update.effective_chat.id, text)
        # ----------
        log_data.append(
            f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] HELLO - {update.effective_chat.id}"
        )
        with open(FILE, "a") as log_file:
            log_file.writelines(log_data)

    def login_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        if update.effective_chat.id not in self.IN_TRANSIT:
            self.IN_TRANSIT[update.effective_chat.id] = dict()
        text = "<b>/email</b> <i>email@domain.com</i>"
        self.send(update.effective_chat.id, text)
        # ----------
        log_data.append(
            f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_L - {update.effective_chat.id}"
        )
        with open(FILE, "a") as log_file:
            log_file.writelines(log_data)

    def email_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        # in case login command was not used
        if update.effective_chat.id not in self.IN_TRANSIT:
            self.IN_TRANSIT[update.effective_chat.id] = dict()
        try:
            self.IN_TRANSIT[update.effective_chat.id]["email"] = update.message["text"].split()[1]
        except Exception as ex:
            text = "<b>/email</b> <i>email@domain.com</i>"
            # ----------
            log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [x] LOGIN_E - {ex}")
        else:
            text = "<b>/pass</b> <i>your_password</i>"
        self.send(update.effective_chat.id, text)
        # ----------
        log_data.append(
            f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_E - {update.effective_chat.id}"
        )
        with open(FILE, "a") as log_file:
            log_file.writelines(log_data)

    def password_function(self, update, CallbackContext):
        now = datetime.now()
        log_data = list()

        if update.effective_chat.id not in self.IN_TRANSIT:
            self.login_function(update, CallbackContext)  # if login or email none was initialized
        else:
            try:
                self.IN_TRANSIT[update.effective_chat.id]["password"] = self.create_password_hashed(
                    update.message["text"].split()[1]
                )
            except Exception as ex:
                text = """<b>/pass</b> <i>your_password</i>"""
                # ----------
                log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [x] LOGIN_P - {ex}")
            else:
                data = self.IN_TRANSIT[update.effective_chat.id]
                try:
                    user_cred_ref = User.objects.get(email=data["email"].lower(), password=data["password"])
                except User.DoesNotExist:
                    text = "<b>Invalid Credentials !</b>"
                    # ----------
                    log_data.append(
                        f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_P - Unsucessful"
                    )
                except Exception as ex:
                    if settings.DEBUG == True:
                        text += f"\n{ex}"
                    else:
                        text = "Unsuccessful."
                        text += "\nError At : <b>Login_P</b>"
                    # ----------
                    log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [x] LOGIN_P - {ex}")
                else:
                    user_cred_ref.telegram_id = update.effective_chat.id
                    user_cred_ref.save()
                    del self.IN_TRANSIT[update.effective_chat.id]
                    text = "Successful."
                    text += "\nTelegram Account added to profile. 😀"
                    # ----------
                    log_data.append(
                        f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_P - Sucessful"
                    )
            finally:
                self.send(update.effective_chat.id, text)
                # ----------
                log_data.append(
                    f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [.] LOGIN_P - {update.effective_chat.id}"
                )
                with open(FILE, "a") as log_file:
                    log_file.writelines(log_data)

    def send_notifications(self, user_id, text):
        self.send(user_id, text)

    def create_password_hashed(self, password):
        sha256_ref = sha256()
        sha256_ref.update(f"ooga{password}booga".encode("utf-8"))
        return str(sha256_ref.digest())

    def run(self, key=None):
        if key == None:
            try:
                self.get_me()
                return True
            except Exception:
                return False
        else:
            try:
                self.updater = Updater(token=self.API_KEY, use_context=True)
                self.dispatcher = self.updater.dispatcher
                self.add_handlers()
                self.updater.start_polling()
                return True
            except Exception:
                raise Exception("Could not start Polling ..")


with open(os.path.join(BASE_DIR, "config", "keys", "TG_KEY.pk"), "r") as secret:
    TG_TOKEN = secret.read().strip()[:-2]
bot = TG_BOT(api_key=TG_TOKEN)
