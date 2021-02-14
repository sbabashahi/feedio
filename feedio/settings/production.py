from feedio.settings.base import *
from feedio.settings.configs import *


SECRET_KEY = os.environ.get('SECRET_KEY', None)

if not SECRET_KEY:
    raise Exception('Add SECRET_KEY env variable, example: export SECRET_KEY=123456')

DEBUG = False

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'feedio',
        'USER': 'feediodb',
        'PASSWORD': 'feediopass',
        'HOST': 'localhost',
        'PORT': ''
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_USE_SSL = True

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'localhost:8000',
)
