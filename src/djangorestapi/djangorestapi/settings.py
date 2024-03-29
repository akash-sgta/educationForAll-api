import os
from pathlib import Path
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =================================================================================================

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "file": {
#             "level": "DEBUG",
#             "class": "logging.FileHandler",
#             "filename": f"{os.path.join(BASE_DIR, "log", "debug.log")}",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file"],
#             "level": "DEBUG",
#             "propagate": True,
#         },
#     },
# }


def check_for_drafts(flag=True):
    # create user specific config and ini
    try:
        fp = open(os.path.join(BASE_DIR, "config", "server.conf"), "r")
        fp.close()  # file found no action required
        return True
    except FileNotFoundError:
        try:
            if flag:
                venv = os.environ["VIRTUAL_ENV"]
            else:
                venv = f"/home/{os.environ['USER']}/education-for-all/venv/"
        except KeyError:
            try:
                venv = os.environ["PYTHONPATH"]
            except KeyError:
                print("[x] Activate VIRTUAL_ENV or set correct PYTHONPATH")
                check = (os.path.join(BASE_DIR, "config", "server.conf"), os.path.join(BASE_DIR, "config", "uwsgi.ini"))
                for one in check:
                    if os.path.exists(one):
                        os.remove(one)
                return False

        # print server.config
        with open(os.path.join(BASE_DIR, "config", "ambiguous", "conf.draft"), "r") as fp_in:
            lines_in = fp_in.readlines()
        with open(os.path.join(BASE_DIR, "config", "server.conf"), "w") as fp_out:
            for line in lines_in:
                line = line.replace("<path>", str(BASE_DIR))
                fp_out.write(line)

        # print uwsgi.ini
        with open(os.path.join(BASE_DIR, "config", "ambiguous", "ini.draft"), "r") as fp_in:
            lines_in = fp_in.readlines()

        with open(os.path.join(BASE_DIR, "config", "uwsgi.ini"), "w") as fp_out:
            for line in lines_in:
                line = line.replace("<path>", str(BASE_DIR))
                line = line.replace("<venv>", venv)
                fp_out.write(line)
            return True


# =================================================================================================

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
try:
    with open(os.path.join(BASE_DIR, "config", "all.pk.json"), "r") as secret_file:
        data = json.load(secret_file)
        SECRET_KEY = data["secret"]
        DEBUG = data["debug"]
        del data
except FileNotFoundError:
    print("[x] Configuration file missing")
    print("[x] Contact ADMIN")
    exit(0)

# Database in configFile
DB_DEFAULT = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "test_databases", "default.db.sqlite3"),
        "TEST": {
            "DEPENDENCIES": ["app_db"],
        },
    }
}

DATABASE_ROUTERS = (
    "routers.db_routers.Django_Auth_Router",
    "routers.db_routers.App_Router",
)

# SECURITY WARNING: don't run with debug turned on in production!
if DEBUG:
    from config.development import ALLOWED_HOSTS
    from config.development import DATABASES as DB_CUSTOM
else:
    from config.production import ALLOWED_HOSTS
    from config.production import DATABASES as DB_CUSTOM
    from config.production import HTTP_SECURED

    if HTTP_SECURED:
        # HTTPS settings
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_SSL_REDIRECT = True

        # HSTS settings
        SECURE_HSTS_SECONDS = 31536000  # 1y
        SECURE_HSTS_RELOAD = True
        SECURE_HSTS_INCLUDE_SUBDOMIANS = True

DATABASES = dict(DB_DEFAULT, **DB_CUSTOM)

# ALLOWED_HOSTS in configFile

# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# create user specific config and ini
# if not check_for_drafts(False):
#     exit(1)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # -----------------------------
    "rest_framework",
    "corsheaders",
    "django_crontab",
    # -----------------------------
    "auth_prime",
    "user_personal",
    "content_delivery",
    "analytics",
    "cronjobs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "djangorestapi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "djangorestapi.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DATA_UPLOAD_MAX_MEMORY_SIZE = 1048576 * 10  # 10MB

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    # -----------------
    "authorization",
    "uauth",
    "content-type",
    "Access-Control-Allow-Origin",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRONTAB_LOCK_JOBS = True
CRONTAB_COMMAND_SUFFIX = "2>&1"  # log error
FILE = os.path.join(BASE_DIR, "log", "cronlog.log")
CRONJOBS = [
    # ('*/1 * * * *', 'cronjobs.cron.test', f'>> {FILE}'), # test module for cronjob
    ("0 * * * *", "cronjobs.cron.token_checker", f">> {FILE}"),  # token expiry checker
    ("*/30 * * * *", "cronjobs.cron.telegram_notification", f">> {FILE}"),  # notifications via TG
    ("0 * * * *", "cronjobs.cron.clear_permalinks", f">> {FILE}"),  # clear invalid links
]
