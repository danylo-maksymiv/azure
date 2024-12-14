import os
from .settings import *
from .settings import BASE_DIR

# SECRET_KEY = os.environ['SECRET']
# if not SECRET_KEY:
#     raise ValueError("SECRET_KEY is not set in environment variables")
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']]
DEBUG = False

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

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'blockchain', 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# MySQL Connection String
conn_str = os.environ['AZURE_MYSQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(';')}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blockchain',
        'HOST': 'blockchain-server.mysql.database.azure.com',
        'USER': 'gtrajjyroa',
        'PASSWORD': 'y$OZ15AqK$fznAgD',
        'PORT': '3306',
    }
}
