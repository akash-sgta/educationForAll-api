import os
from pathlib import Path
import json

## ================================================================================================= ##

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

## ================================================================================================= ##

# Logging

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

## ================================================================================================= ##

# def check_for_drafts(flag=True):
#     # create user specific config and ini
#     try:
#         fp = open(os.path.join(BASE_DIR, "config", "server.conf"), "r")
#         fp.close()  # file found no action required
#         return True
#     except FileNotFoundError:
#         try:
#             if flag:
#                 venv = os.environ["VIRTUAL_ENV"]
#             else:
#                 venv = f"/home/{os.environ['USER']}/education-for-all/venv/"
#         except KeyError:
#             try:
#                 venv = os.environ["PYTHONPATH"]
#             except KeyError:
#                 print("[x] Activate VIRTUAL_ENV or set correct PYTHONPATH")
#                 check = (os.path.join(BASE_DIR, "config", "server.conf"), os.path.join(BASE_DIR, "config", "uwsgi.ini"))
#                 for one in check:
#                     if os.path.exists(one):
#                         os.remove(one)
#                 return False

#         # print server.config
#         with open(os.path.join(BASE_DIR, "config", "ambiguous", "conf.draft"), "r") as fp_in:
#             lines_in = fp_in.readlines()
#         with open(os.path.join(BASE_DIR, "config", "server.conf"), "w") as fp_out:
#             for line in lines_in:
#                 line = line.replace("<path>", str(BASE_DIR))
#                 fp_out.write(line)

#         # print uwsgi.ini
#         with open(os.path.join(BASE_DIR, "config", "ambiguous", "ini.draft"), "r") as fp_in:
#             lines_in = fp_in.readlines()

#         with open(os.path.join(BASE_DIR, "config", "uwsgi.ini"), "w") as fp_out:
#             for line in lines_in:
#                 line = line.replace("<path>", str(BASE_DIR))
#                 line = line.replace("<venv>", venv)
#                 fp_out.write(line)
#             return True

## ================================================================================================= ##

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret !
# Reading data from congif file
try:
    with open(os.path.join(BASE_DIR, "config.json"), "r") as config:

        data = json.load(config)
        DEBUG = data["debug"]
        # SECURITY WARNING: don't run with debug turned on in production!
        if data["server"] == "development":
            SECRET_KEY = data["development"]["secret"]
            DATABASES = data["development"]["database"]
            ALLOWED_HOSTS = data["development"]["allowed_hosts"]
        else:
            SECRET_KEY = data["production"]["secret"]
            DATABASE_ROUTERS = (
                "database.router.Django_Auth",
                "database.router.App",
            )
            DATABASES = data["production"]["database"]

            ALLOWED_HOSTS = data["production"]["allowed_hosts"]

            if data["production"]["http_secured"]:
                # HTTPS settings
                SESSION_COOKIE_SECURE = True
                CSRF_COOKIE_SECURE = True
                SECURE_SSL_REDIRECT = True

                # HSTS settings
                SECURE_HSTS_SECONDS = 31536000  # 1y
                SECURE_HSTS_RELOAD = True
                SECURE_HSTS_INCLUDE_SUBDOMIANS = True

        del data
except FileNotFoundError:
    print("[x] Configuration file missing")
    print("[x] Contact ADMIN")
    exit(0)

## ================================================================================================= ##


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
    "utilities",  # Important
    "identityAccessManagement",
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

ROOT_URLCONF = "educationForAll.urls"

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

WSGI_APPLICATION = "educationForAll.wsgi.application"

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
USE_TZ = False
TIME_ZONE = "Asia/Kolkata"

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
    "content-type",
    "Access-Control-Allow-Origin",
]

# CRONTAB_LOCK_JOBS = True
# CRONTAB_COMMAND_SUFFIX = "2>&1"  # log error
# FILE = os.path.join(BASE_DIR, "log", "cronlog.log")
# CRONJOBS = [
#     # ('*/1 * * * *', 'cronjobs.cron.test', f'>> {FILE}'), # test module for cronjob
#     ("0 * * * *", "cronjobs.cron.token_checker", f">> {FILE}"),  # token expiry checker
#     ("*/30 * * * *", "cronjobs.cron.telegram_notification", f">> {FILE}"),  # notifications via TG
#     ("0 * * * *", "cronjobs.cron.clear_permalinks", f">> {FILE}"),  # clear invalid links
# ]
