"""
Django settings for Shopyaar - Modern Persian E-commerce
"""

from pathlib import Path
import os

from dotenv import load_dotenv
import dj_database_url


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-key-change-in-production-shopyaar-2026'
)

DEBUG = os.environ.get(
    'DEBUG',
    'True'
).lower() in ('true', '1', 'yes')


ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1,.onrender.com'
    ).split(',')
    if host.strip()
]


# ============================================================
# APPLICATION DEFINITION
# ============================================================

INSTALLED_APPS = [

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    # Third Party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',

    # Local Apps
    'store',
    'accounts',
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',
]


# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = 'shopyaar.urls'


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [

    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates'
        ],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

                'store.context_processors.cart_context',

            ],
        },
    },
]


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = 'shopyaar.wsgi.application'


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.environ.get('DATABASE_URL')


if DATABASE_URL:

    DATABASES = {

        'default': dj_database_url.config(

            default=DATABASE_URL,

            conn_max_age=600,

            ssl_require=True,

        )
    }

else:

    DATABASES = {

        'default': {

            'ENGINE': 'django.db.backends.sqlite3',

            'NAME': BASE_DIR / 'db.sqlite3',

        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator'
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator'
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator'
    },

]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = 'fa'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)


# ============================================================
# CLOUDINARY CONFIGURATION
# ============================================================

CLOUDINARY_CLOUD_NAME = os.environ.get(
    'CLOUDINARY_CLOUD_NAME',
    ''
)

CLOUDINARY_API_KEY = os.environ.get(
    'CLOUDINARY_API_KEY',
    ''
)

CLOUDINARY_API_SECRET = os.environ.get(
    'CLOUDINARY_API_SECRET',
    ''
)


CLOUDINARY_STORAGE = {

    'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,

    'API_KEY': CLOUDINARY_API_KEY,

    'API_SECRET': CLOUDINARY_API_SECRET,

    'EXCLUDE_DELETE_ORPHANED_MEDIA': False,

    'PREFIX': 'shopyaar',

}


# ============================================================
# CLOUDINARY CONFIGURATION (override)
# ============================================================

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get(
        'CLOUDINARY_CLOUD_NAME'
    ),

    'API_KEY': os.environ.get(
        'CLOUDINARY_API_KEY'
    ),

    'API_SECRET': os.environ.get(
        'CLOUDINARY_API_SECRET'
    ),

    'SECURE': True,

    'MEDIA_TAG': 'shopyaar',

    'PREFIX': 'shopyaar/',
}


# ============================================================
# DJANGO FILE STORAGES
# ============================================================

STORAGES = {

    'default': {

        'BACKEND':
            'cloudinary_storage.storage.MediaCloudinaryStorage',

    },

    'staticfiles': {

        'BACKEND':
            'whitenoise.storage.CompressedManifestStaticFilesStorage',

    },

}


# ============================================================
# MEDIA
# ============================================================

MEDIA_URL = '/media/'


# ============================================================
# CLOUDINARY IMAGE SETTINGS
# ============================================================

CLOUDINARY_IMAGE_FORMATS = [

    'jpg',

    'jpeg',

    'png',

    'webp',

    'gif',

    'bmp',

    'tiff',

]


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# DJANGO SITES
# ============================================================

SITE_ID = 1


# ============================================================
# AUTHENTICATION
# ============================================================

AUTHENTICATION_BACKENDS = [

    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',

]


LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/'

ACCOUNT_LOGOUT_ON_GET = True

ACCOUNT_EMAIL_VERIFICATION = 'none'


# ============================================================
# ALLAUTH
# ============================================================

ACCOUNT_LOGIN_METHODS = {
    'email'
}

ACCOUNT_SIGNUP_FIELDS = [
    'email*'
]

SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_LOGIN_ON_GET = True


# ============================================================
# GOOGLE OAUTH
# ============================================================

SOCIALACCOUNT_PROVIDERS = {

    'google': {

        'SCOPE': [

            'profile',

            'email',

        ],

        'AUTH_PARAMS': {

            'access_type': 'online',

            'prompt': 'select_account',

        },

        'APP': {

            'client_id': os.environ.get(
                'GOOGLE_CLIENT_ID',
                ''
            ),

            'secret': os.environ.get(
                'GOOGLE_CLIENT_SECRET',
                ''
            ),

            'key': '',

        },
    }
}


# ============================================================
# ADMIN EMAIL
# ============================================================

ADMIN_EMAIL = 'shapyaar@gmail.com'


# ============================================================
# STRIPE
# ============================================================

STRIPE_PUBLISHABLE_KEY = os.environ.get(
    'STRIPE_PUBLISHABLE_KEY',
    ''
)

STRIPE_SECRET_KEY = os.environ.get(
    'STRIPE_SECRET_KEY',
    ''
)


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.environ.get(
    'TELEGRAM_BOT_TOKEN',
    ''
)

TELEGRAM_CHAT_ID = os.environ.get(
    'TELEGRAM_CHAT_ID',
    ''
)


# ============================================================
# PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = 'DENY'


# ============================================================
# CSRF / TRUSTED ORIGINS
# ============================================================

CSRF_TRUSTED_ORIGINS = [

    origin.strip()

    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        ''
    ).split(',')

    if origin.strip()

]


# ============================================================
# MESSAGE TAGS
# ============================================================

from django.contrib.messages import constants as messages


MESSAGE_TAGS = {

    messages.DEBUG: 'debug',

    messages.INFO: 'info',

    messages.SUCCESS: 'success',

    messages.WARNING: 'warning',

    messages.ERROR: 'error',

}
