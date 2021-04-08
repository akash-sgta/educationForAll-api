DJANGO_PROJ_S_KEY = 'i^!7)$$#6f655lfi&o=0^o-yo9-rt1obsujnw*3@lz^0nyc!l6'
DEBUG_STATUS = True

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

'''DB_SETTINGS = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  os.path.join(BASE_DIR,'test.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}'''

DB_SETTINGS = {
    'default' : {
        'ENGINE': "django.db.backends.mysql",
        'NAME':  "projectDB",
        'USER': "admin",
        'PASSWORD': "GANDUgandu",
        'HOST': "projectdatabase1.czbsimzcrcxe.ap-south-1.rds.amazonaws.com",
        'PORT': "6969"
    }
}

YT_API_PUBLIC = "AIzaSyBOdQWR5phznYaAOIL6uJQQDzKH3lwWI1o"
YT_API_USER = None