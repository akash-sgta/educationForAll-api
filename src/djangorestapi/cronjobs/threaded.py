import threading
import platform
import os
from time import sleep

from bot_auth_token import *
from bot_tg_logger import *
from bot_tg_notification import *

# ------------------------------------------------------------

stop_thread = False

class Threading_1(Telegram_Bot, threading.Thread):
    pass

class Threading_2(Notification_Handler, threading.Thread):
    pass

class Threading_3(Token_Handler, threading.Thread):
    pass

if __name__ == "__main__":

    if(platform.system().upper() == 'Windows'.upper()):
        os.system('cls')
    else:
        os.system('clear')
    print("*****************************************\n\n")
    print("[.] Starting automatron...\n\n")
    sleep(2)

    try:
        thread_1 = Threading_1(TG_TOKEN, DB_URL)
        print("[T] Telegram Bot started...")
        sleep(1)
        thread_1.start()
    
    except Exception as ex:
        print(f"[T] EX : {ex}")
        print("[T] Telegram Bot stopped...")

    try:
        thread_2 = Threading_2(TG_TOKEN, DB_URL)
        print("[N] Notification Bot started...")
        sleep(1)
        thread_2.start()
    
    except Exception as ex:
        print(f"[N] EX : {ex}")
        print("[N] Notification Bot stopped...")

    try:
        thread_3 = Threading_3(TG_TOKEN, DB_URL)
        print("[t] Token Bot started...")
        sleep(1)
        thread_3.start()
    
    except Exception as ex:
        print(f"[t] EX : {ex}")
        print("[t] Token Bot stopped...")
    
    try:
        thread_1.join()
        thread_2.join()
        thread_3.join()
    except Exception:
        pass

    print("\n\n[!] Thank you for using out automatron...\n\n")
    print("\n\n*****************************************\n\n")
    