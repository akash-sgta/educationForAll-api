import os
from pathlib import Path

# ----------OTHERS--------------

ALLOWED_HOSTS = ["*"]

# -----------DATABASE-------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = dict()
DATABASES["auth_db"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "test_databases", "djangoauth.db.sqlite3"),
    "TEST": {
        "DEPENDENCIES": [],
    },
}
DATABASES["app_db"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "test_databases", "app.db.sqlite3"),
    "TEST": {
        "DEPENDENCIES": [],
    },
}
