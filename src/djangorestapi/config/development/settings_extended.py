from pathlib import Path
import os

# ----------OTHERS--------------

ALLOWED_HOSTS = ("127.0.0.1", "localhost")

# -----------DATABASE-------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_ROUTERS = (
    "routers.db_routers.Django_Auth_Router",
    "routers.db_routers.App_Router",
)

DATABASES = dict()
DATABASES["default"] = {}
DATABASES["auth_db"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "test_databases", "djangoauth.db.sqlite3"),
}
DATABASES["app_db"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "test_databases", "app.db.sqlite3"),
}
