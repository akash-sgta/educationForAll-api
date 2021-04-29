from pathlib import Path
import os

# ----------OTHERS--------------

ALLOWED_HOSTS = (
    "*",
)

# ----------SSL--------------

HTTP_SECURED = False
if(HTTP_SECURED):
    # HTTPS settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

    #HSTS settings
    SECURE_HSTS_SECONDS = 31536000 # 1y
    SECURE_HSTS_RELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMIANS = True

# -----------DATABASE-------------

DATABASE_ROUTERS = (
    'routers.db_routers.Django_Auth_Router',
    'routers.db_routers.App_Router',
)

CRED = (
    ("JCGbVPW0pV", "wyJF99q5ym"),
    ("xNYSHtH8zf", "pKCUPv0Xho")
)

DB_SETTINGS = dict()
DB_SETTINGS['default'] = {}
DB_SETTINGS['auth_db'] = {
    'ENGINE': "django.db.backends.mysql",
    'OPTIONS': {
        'sql_mode': 'traditional',
    },
    'NAME':  CRED[0][0],
    'USER': CRED[0][0],
    'PASSWORD': CRED[0][1],
    'HOST': "remotemysql.com",
    'PORT': "3306"
}
DB_SETTINGS['app_db'] = {
    'ENGINE': "django.db.backends.mysql",
    'OPTIONS': {
        'sql_mode': 'traditional',
    },
    'NAME':  CRED[1][0],
    'USER': CRED[1][0],
    'PASSWORD': CRED[1][1],
    'HOST': "remotemysql.com",
    'PORT': "3306"
}