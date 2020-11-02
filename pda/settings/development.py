from .base import *

DEBUG = True

ALLOWED_HOSTS += ['localhost', '127.0.0.1', ]

INSTALLED_APPS += [
    'debug_toolbar',
    ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    },
    'session_db': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('SESSION_DB_NAME'),
        'USER': config('SESSION_DB_USER'),
        'PASSWORD': config('SESSION_DB_PASSWORD'),
        'HOST': config('SESSION_DB_HOST'),
        'PORT': config('SESSION_DB_PORT'),
    }
}

INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]