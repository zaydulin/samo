import os.path
import sys
from pathlib import Path
from string import  ascii_lowercase, ascii_uppercase, digits
from django.utils.translation import gettext_lazy as _
import logging
from environs import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

### setting up env
env = Env()
env.read_env()
from typing import Any, Dict

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1g&%io*&h%dr3^(@t%l6yw%-ad8dm_+uou3!v^c0eek=ga@(-l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Library (Бибилиотеки)
    'ckeditor',
    'ckeditor_uploader',
    'tinymce',
    #'debug_toolbar',
    "ipware",
    'channels',
    'crispy_forms',
    'nested_admin',
    'django_ace',
    'multiselectfield',
    'rosetta',
    # app (Приложения)
    'webmain.apps.WebmainConfig',
    'moderation.apps.ModerationConfig',
    'useraccount.apps.UseraccountConfig',
    'integration_payment.apps.IntegrationPaymentConfig',
    'lms.apps.LmsConfig',
    'developers.apps.DevelopersConfig',
    'conference.apps.ConferenceConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'useraccount.middlewares.ActiveUserMiddleware',
    '_project.domain_urls_middleware.DomainURLsMiddleware',

]
ADMIN_URL = 'developer_management/'

SITE_ID = 1

ROOT_URLCONF = '_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '_templates')],
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

WSGI_APPLICATION = '_project.wsgi.application'
ASGI_APPLICATION = '_project.asgi.application'

RANDOM_MOVIE_URL_CHARSET = f'{ascii_lowercase}{ascii_uppercase}{digits}'
RANDOM_MOVIE_URL_LENGTH = 32
RANDOM_MOVIE_URL_MAX_TRIES = 42

RANDOM_PLAYLIST_URL_CHARSET = f'{ascii_lowercase}{ascii_uppercase}{digits}'
RANDOM_PLAYLIST_URL_LENGTH = 16
RANDOM_PLAYLIST_URL_MAX_TRIES = 28
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases



# Настройки GrapesJS
GRAPESJS_EDITOR_CONFIG = {
    'height': '100vh',  # Высота редактора
    'container': '#gjs',  # ID контейнера
    'fromElement': True,  # Загружать контент из контейнера
    'storageManager': False,  # Отключаем встроенное хранилище
    'plugins': ['gjs-preset-webpage'],  # Базовый набор плагинов
    'canvas': {
        'styles': [
            '/static/css/your-styles.css',  # Ваши стили
        ],
    },
    'blockManager': {
        'appendTo': '#blocks',
        'blocks': [
            {
                'id': 'section',
                'label': 'Section',
                'category': 'Basic',
                'content': '<section class="section"><div class="container"></div></section>',
            },
        ]
    },
}



INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/
LOCALE_PATHS = [
    BASE_DIR / '_locale',
]
LANGUAGE_CODE = 'ru'

LANGUAGES = (
    ('ru', _('Russian')),
    ('en', _('English')),
)

TIME_ZONE = 'Europe/Samara'

USE_I18N = True

USE_TZ = True

LOGIN_URL = '/ru/login/'

AUTH_USER_MODEL = 'useraccount.Profile'

JAZZMIN_SETTINGS = {
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": "admin/js/custom_admin.js",
    "site_brand": " ",
    'site_logo': 'admin/img/logo_shop_cms.webp',
    "site_icon": 'admin/img/favicon.svg',
    "navigation_expanded": False,
    "related_modal_active": False,
    "changeform_format": "vertical_tabs",
    # Order of apps and models
    "order_with_respect_to": [
        "integration_payment",
        "-",
        "moderation",
    ],

    "hide_apps": ['sites', 'auth'],
    "hide_models": ["admin.LogEntry"],
    "icons": {
        "developer": "fas fa-handshake",
        #"developer.model3": "fas fa-warehouse",
        "integration_delivery": "fas fa-truck",
        "integration_import": "fa fa-upload",
        "integration_payment": "fa fa-university",
        "useraccount": "fa fa-users",
        "shop": "fas fa-store",
        "moderation": "fa fa-users",
        "webmain": "fa fa-globe",
        "auth": "fas fa-users-cog",
        "Языки": "fas fa-users-cog",
    },
    "custom_links": {
        "webmain": [
            {
                "name": "Домены",
                "url": "/developer_management/sites/site/",
                "permissions": ["sites.site"]
            }

        ],
        "useraccount": [
            {
                "name": "Группы",
                "permissions": ["auth.group"]
            },

        ]
    },
}
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


STATIC_URL = '/_static/'
STATICFILES_DIRS = ('_static',)
#STATIC_ROOT = os.path.join(BASE_DIR, '_static')

MEDIA_URL = '/_media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '_media')



# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

SITE_ID = 1

SESSION_COOKIE_DOMAIN = ".mentro.store"  # Доступ ко всем поддоменам
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_SECURE = True  # Если у вас HTTPS, иначе False
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"  # Или ваша текущая БД


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'csv_upload.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}


REDIS_HOST = env.str('DJANGO_REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(env.str('DJANGO_REDIS_HOST', 'localhost'), 6379)]
        },
    },
}
REDIS_PORT_STR = str(REDIS_PORT)
CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT_STR + '/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout' : 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT_STR + '/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASKS_PREFER_MULTI_PROCESSING = True
CELERYD_CONCURRENCY = 8

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"


CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # put this to force next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                # put the name of your editor.ui.addButton here
                'Preview',
                'Maximize',

            ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
        # 'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}


# Настройки TinyMCE
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': 1120,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'plugins': 'image,imagetools,link,lists,table,code',
    'toolbar': 'undo redo | bold italic underline | alignleft aligncenter alignright | bullist numlist | link image | code',
    'image_advtab': True,
    'images_upload_url': '/tinymce/image_upload/',  # Точный путь
    'images_upload_credentials': True,
}

# Путь для загрузки изображений
TINYMCE_MEDIA_ROOT = os.path.join(BASE_DIR, 'media/tinymce')
TINYMCE_MEDIA_URL = '/media/tinymce/'


RANDOM_URL_CHARSET = f'{ascii_lowercase}{ascii_uppercase}{digits}'
RANDOM_URL_LENGTH = 32
RANDOM_URL_MAX_TRIES = 42

DATA_UPLOAD_MAX_MEMORY_SIZE = 1073741824  # 1 GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 1073741824  # 1 GB
