import os
from pathlib import Path

# ----------------------------------------

with open(os.path.join(BASE_DIR, 'TG_KEY.txt'), 'r') as key_file:
    TG_TOKEN = key_file.read().strip()[:-2]
DB_URL = os.path.join(Path(__file__).resolve().parent.parent, 'app.db.sqlite3')

# ----------------------------------------