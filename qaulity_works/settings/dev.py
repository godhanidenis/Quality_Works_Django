from .base import *

SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE':config("DB_ENGINE"),
        'NAME': config("DB_NAME"),
        'HOST': config("DB_HOST"),
        'PORT': config("DB_PORT"),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators




