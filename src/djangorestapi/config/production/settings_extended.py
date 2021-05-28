from pathlib import Path
import os

# ----------OTHERS--------------

ALLOWED_HOSTS = (
    "127.0.0.1",
    "localhost",
)

# ----------SSL--------------

HTTP_SECURED = False

# -----------DATABASE-------------

BASE_DIR = Path(__file__).resolve().parent.parent
with open(os.path.join(BASE_DIR, "keys", "DB_KEY.pk"), "r") as db:
    text = db.readlines()
    for i in range(len(text)):
        text[i] = text[i].strip()[1:-2]

DATABASES = dict()
DATABASES["auth_db"] = {
    "ENGINE": "django.db.backends.mysql",
    "OPTIONS": {
        "sql_mode": "traditional",
    },
    "NAME": text[0] + "1",
    "USER": text[0],
    "PASSWORD": text[1],
    "HOST": text[2],
    "PORT": text[3],
    "TEST": {
        "DEPENDENCIES": [],
    },
}
DATABASES["app_db"] = {
    "ENGINE": "django.db.backends.mysql",
    "OPTIONS": {
        "sql_mode": "traditional",
    },
    "NAME": text[0] + "2",
    "USER": text[0],
    "PASSWORD": text[1],
    "HOST": text[2],
    "PORT": text[3],
    "TEST": {
        "DEPENDENCIES": [],
    },
}
