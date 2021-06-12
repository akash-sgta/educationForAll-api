import json
import os
from pathlib import Path

# ----------OTHERS--------------

ALLOWED_HOSTS = ("localhost", "127.0.0.1")

# ----------SSL--------------

HTTP_SECURED = False

# -----------DATABASE-------------

BASE_DIR = Path(__file__).resolve().parent.parent
try:
    with open(os.path.join(BASE_DIR, "config", "all.pk.json"), "r") as secret_file:
        data = json.load(secret_file)
        DB = data["database"]
        del data
except FileNotFoundError:
    print("[x] Configuration file missing")
    print("[x] Contact ADMIN")
    exit(0)
else:
    DATABASES = dict()
    DATABASES["auth_db"] = {
        "ENGINE": "django.db.backends.mysql",
        "OPTIONS": {
            "sql_mode": "traditional",
        },
        "NAME": DB["name"][0],
        "USER": DB["user"],
        "PASSWORD": DB["password"],
        "HOST": DB["host"],
        "PORT": DB["port"],
        "TEST": {
            "DEPENDENCIES": [],
        },
    }
    DATABASES["app_db"] = {
        "ENGINE": "django.db.backends.mysql",
        "OPTIONS": {
            "sql_mode": "traditional",
        },
        "NAME": DB["name"][1],
        "USER": DB["user"],
        "PASSWORD": DB["password"],
        "HOST": DB["host"],
        "PORT": DB["port"],
        "TEST": {
            "DEPENDENCIES": [],
        },
    }
