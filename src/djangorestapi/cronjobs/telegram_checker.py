from pathlib import Path
from .automatron import (
    TG_BOT,
    Database
)
import os
import sys

# ---------------------------------------------

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    TELEGRAM_KEY = os.path.join(BASE_DIR, 'config', 'ambiguous', 'TG_KEY.txt')
    DATABASE = os.path.join(BASE_DIR, 'test_databases', 'app.db.sqlite3')

    with open(TELEGRAM_KEY, 'r') as secret:
        TG_TOKEN = secret.read().strip()[:-2]
    print(TG_TOKEN)

    exit(0)
    bot = TG_BOT(TG_TOKEN)
    db = Database(DATABASE)

    try:
        bot.run(1)
    except KeyboardInterrupt as ex:
        sys.exit('Keyboard Interrupt')