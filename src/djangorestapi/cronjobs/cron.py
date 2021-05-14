from auth_prime.models import (
    User_Token_Table,
)

from user_personal.models import (
    User_Notification_Int,
)

import os
from pathlib import Path
from datetime import datetime, timedelta

from cronjobs.bot import bot

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = os.path.join(BASE_DIR, 'log', 'cronlog.log')

# ---------------------------------------------------------

def telegram_notification():
    print("\n---------------------------")
    print("TELEGRAM_NOTIFICATION")
    log_data = list()
    now = datetime.now()

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
        log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: NOTIFICATION CRONJOB\t\t:: [.] Notification Sent {count}")

    else:
        log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: NOTIFICATION CRONJOB\t\t:: [*] Notification - Could Not Start")
    
    with open(FILE, 'a') as log_file:
        log_file.writelines(log_data)

def token_checker():
    print("\n---------------------------")
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
    log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TOKEN CRONJOB\t\t:: [.] Tokens expired : {token_delete_count}")
    with open(FILE, 'a') as log_file:
        log_file.writelines(log_data)

def test():
    print("\n---------------------------")
    print("TEST")
    now = datetime.now()
    log_data = list()
    
    log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TEST CRONJOB\t\t:: [*] POPPED")
    with open(FILE, 'a') as log_file:
        log_file.writelines(log_data)