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

# -----------------------------------------------

HOST = (
    "jcgbvpw0pv.czbsimzcrcxe.ap-south-1.rds.amazonaws.com",
    "3306"
)

# -----------------------------------------------

DB_SETTINGS = dict()
DB_SETTINGS['default'] = {}
DB_SETTINGS['auth_db'] = {
    'ENGINE': "django.db.backends.mysql",
    'OPTIONS': {
        'sql_mode': 'traditional',
    },
    'NAME':  "JCGbVPW0pV1",
    'USER': "JCGbVPW0pV",
    'PASSWORD': "wyJF99q5ym",
    'HOST': HOST[0],
    'PORT': HOST[1]
}
DB_SETTINGS['app_db'] = {
    'ENGINE': "django.db.backends.mysql",
    'OPTIONS': {
        'sql_mode': 'traditional',
    },
    'NAME':  "JCGbVPW0pV2",
    'USER': "JCGbVPW0pV",
    'PASSWORD': "wyJF99q5ym",
    'HOST': HOST[0],
    'PORT': HOST[1]
}