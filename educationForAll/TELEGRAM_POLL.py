from django.conf import settings
import django

from djangorestapi.settings import DATABASES, INSTALLED_APPS, SECRET_KEY, DATABASE_ROUTERS
settings.configure(
    DATABASES=DATABASES,
    INSTALLED_APPS=INSTALLED_APPS,
    SECRET_KEY=SECRET_KEY,
    DATABASE_ROUTERS=DATABASE_ROUTERS
)
django.setup()

import os
from pathlib import Path
from datetime import datetime, timedelta
from time import sleep

from cronjobs.bot import bot

BASE_DIR = Path(__file__).resolve().parent
FILE = os.path.join(BASE_DIR, 'log', 'cronlog.log')

# ------------------------------------

def telegram_bot():
    print("\n---------------------------")
    print("TELEGRAM_BOT")
    print("check for -- cronjob.log")
    now = datetime.now()
    log_data = list()

    if(bot.run()):
        try:
            # ----------
            log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [*] POLLING - Started..")
            
            bot.run('START_POLLING')
        except Exception as ex:
            # ----------
            log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [*] POLLING - {ex}")
    else:
        log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TELEGRAM BOT CRONJOB\t\t:: [*] POLLING - Could Not Start")
    
    with open(FILE, 'a') as log_file:
        log_file.writelines(log_data)

if __name__ == "__main__":
    try:
        telegram_bot()
    except KeyboardInterrupt:
        print("Closing bot in 2 secs...")
        sleep(3)