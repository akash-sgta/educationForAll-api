import os
from pathlib import Path

# -----------------------------------------------

DB_URL = os.path.join(Path(__file__).resolve().parent.parent, 'test.sqlite3')
TG_TOKEN = '1470401355:AAErhMgyyWSAerh_JfN7BkdPwP37D1dl00U'
DEBUG = True