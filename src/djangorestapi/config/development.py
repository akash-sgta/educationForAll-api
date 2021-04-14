from pathlib import Path
import os

# ----------OTHERS--------------

ALLOWED_HOSTS_ = (
    '127.0.0.1',
    'localhost',
    #'jass.xyx',
    #'www.jass.xyx',
)

# -----------DATABASE-------------

BASE_DIR_ = Path(__file__).resolve().parent.parent

DATABASE_ROUTERS = (
    'routers.db_routers.Django_Auth_Router',
    'routers.db_routers.App_Router',
)

DB_SETTINGS = dict()
DB_SETTINGS['default'] = {}
DB_SETTINGS['auth_db'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME':  os.path.join(BASE_DIR_,'djangoauth.db.sqlite3'),
}
DB_SETTINGS['app_db'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME':  os.path.join(BASE_DIR_,'app.db.sqlite3'),
}
