from pathlib import Path
import os
from hashlib import sha256
from time import sleep
from datetime import datetime, timedelta

from database_sql import Database

# ----------------------------------------

def main():
    BASE_DIR = Path(__file__).resolve().parent.parent
    LOG_PATH = os.path.join(BASE_DIR, 'log', 'token_checker.log')

    with open(os.path.join(BASE_DIR, 'config', 'debug.txt'), 'r') as debug_status:
        DEBUG = debug_status.read()[1:-1]
        if(DEBUG == 'True'):
            DEBUG = True
        else:
            DEBUG = False
    if(DEBUG):
        db = Database()
        db.type = 'sqlite'
        db.data = {
            "database" : os.path.join(BASE_DIR, 'test_databases', 'app.db.sqlite3')
        }
    else:
        db.type = 'mysql'
        db.data = {
            'database':  "appDB",
            'user': "admin",
            'password': "GANDUgandu",
            'host': "projectdatabase1.czbsimzcrcxe.ap-south-1.rds.amazonaws.com",
            'port' : "6969"
        }
    
    db.connect()
    returnData = db.select_sql(
        appName = 'auth_prime',
        tableName = 'user_token_table',
        columnName = ['token_id', 'token_start']
    )
    db.disconnect()
    if(len(returnData) < 1):
        with open(LOG_PATH, 'a') as log:
            log.write("[.] Tokens left : 0\n")
    else:
        with open(LOG_PATH, 'a') as log:
            log.write(f"[.] Tokens left : {len(returnData)}\n")
        for data in returnData:
            now = datetime.now()
            then = datetime.strptime(data[1].split(".")[0], "%Y-%m-%d %H:%M:%S") + timedelta(hours=48)

            if(now > then):
                db.connect()
                db.delete_sql(
                    appName = 'auth_prime',
                    tableName = 'user_token_table',
                    condition = f'''token_id = {data[0]}'''
                )
                db.commit()
                db.disconnect()

# main()