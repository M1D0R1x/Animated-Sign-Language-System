import os
import dj_database_url
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3k7=!d39#4@&5a6to&4==j(c^v0(vv91cj5+9e8+d4&+01jb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False# Set to False for production

ALLOWED_HOSTS = ['.vercel.app', '.now.sh', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'animated_sign_language_system',
]

ROOT_URLCONF = 'animated_sign_language_system.urls'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'animated_sign_language_system.wsgi.application'

# Database configuration using Neon database URL
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://neondb_owner:npg_e7w0pvXgEqxW@ep-divine-unit-a1jsk8qe-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom path for synonyms file
SYNONYM_PATH = os.path.join("synonyms.json")

# Vercel-specific settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# MUX Configuration
MUX_TOKEN_ID = os.environ.get('MUX_TOKEN_ID', '0a31dc59-06d7-4788-ae96-0e031f54affc')
MUX_TOKEN_SECRET = os.environ.get('MUX_TOKEN_SECRET', '4tjPx3iBV3X8shr/tNudreJL7Ogdk+1wIo1q5C/IUjbXmuzw7a53JjFoOubb7ZwhN7RzEEhyfwG')
MUX_STREAM_URL = 'https://stream.mux.com/'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'animated_sign_language_system': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
