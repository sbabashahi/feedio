from feedio.settings.base import *
from feedio.settings.configs import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4e+8-0sobmf2z53y^%^*ew011o#ih)zkl4-98e(x4&6-3*^4e('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'feediodb',
        'USER': 'feedio',
        'PASSWORD': 'feediopass',
        'HOST': 'localhost',
        'PORT': ''
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CORS_ORIGIN_ALLOW_ALL = True
