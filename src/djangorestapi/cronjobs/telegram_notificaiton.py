from bot_telegram import TG_BOT

from pathlib import Path
import os
import sys

# ---------------------------------------------

def main():
    os.system('clear')

    BASE_DIR = Path(__file__).resolve().parent.parent
    LOG_PATH = os.path.join(BASE_DIR, 'log', 'telegram_notification.log')

    with open(os.path.join(BASE_DIR, 'config', 'ambiguous', 'TG_KEY.txt'), 'r') as secret:
        TG_TOKEN = secret.read().strip()[:-2]
    bot = TG_BOT(api_key=TG_TOKEN)
    if(bot.run() == True):
        bot.connect()
        returnedData = bot.select_sql(
            appName = 'user_personal',
            tableName = 'user_notification_int',
            columnName = ['id', 'notification_id_id', 'user_credential_id_id'],
            condition = 'prime_1 = 0'
        )
        if(len(returnedData) > 0):
            with open(LOG_PATH, 'a') as log:
                log.write(f"[.] Notification Left : {len(returnedData)}\n")

            for data in returnedData[:100]:
                user_tg = bot.select_sql(
                    appName = 'auth_prime',
                    tableName = 'user_credential',
                    columnName = ['user_tg_id'],
                    condition = f'''user_credential_id = {data[2]}'''
                )
                if(user_tg[0][0] in (None, "", False, 0, "NULL")):
                    tries = bot.select_sql(
                        appName = 'user_personal',
                        tableName = 'user_notification_int',
                        columnName = ['tries'],
                        condition = f'''id = {data[0]}'''
                    )[0][0]
                    bot.update_sql(
                        appName = 'user_personal',
                        tableName = 'user_notification_int',
                        columnChanges = f'''tries = {int(tries)+1}''',
                        condition = f'''id = {data[0]}'''
                    )
                    bot.commit()

                    with open(LOG_PATH, 'a') as log:
                        log.write(f"[x] TG NOT LINKED\n")
                else:
                    notification = bot.select_sql(
                                    appName = 'user_personal',
                                    tableName = 'notification',
                                    columnName = ['notification_body'],
                                    condition = f'''notification_id = {data[1]}'''
                                )
                    user_tg = user_tg[0][0]
                    notification = notification[0][0]
                    bot.send_notifications(user_tg, notification)
                    bot.update_sql(
                        appName = 'user_personal',
                        tableName = 'user_notification_int',
                        columnChanges = f'''prime_1 = 1''',
                        condition = f'''id = {data[0]}'''
                    )
                    bot.commit()
        else:
            with open(LOG_PATH, 'a') as log:
                log.write("[.] Notification Left : 0\n")
        bot.disconnect()

main()