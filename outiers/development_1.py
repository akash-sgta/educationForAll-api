DJANGO_PROJ_S_KEY = 'i^!7)$$#6f655lfi&o=0^o-yo9-rt1obsujnw*3@lz^0nyc!l6'
DEBUG_STATUS = True


from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

DB_SETTINGS = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  os.path.join(BASE_DIR,'test.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },

    'authDB': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR,'auth.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },

    'usersDB': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR,'users.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },

    'contentDB': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR,'content.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

YT_API_PUBLIC = "AIzaSyBOdQWR5phznYaAOIL6uJQQDzKH3lwWI1o"
YT_API_USER = None

REST_API_S_KEY = "rcu5*9&8uY-_Ykc?7E5x&Cuq+=J3GWvsEGa**N^NFr-4=#pNJw7N5Dvfw_mAbXXH"