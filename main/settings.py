# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
from datetime import datetime
from os.path import join, abspath, dirname

here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)

import djcelery
djcelery.setup_loader()

import mongoengine
#from mongoengine.django.sessions import MongoSession
from celery.schedules import crontab

sys.path.insert(0, os.getcwd())

_rootpath = os.environ.get('ROOTPATH', './tmp')
_dbpath = os.environ.get('DBPATH', _rootpath)
_logpath = os.environ.get('LOGPATH', _rootpath)
_host = os.environ.get('HOSTNAME', 'localhost')
_dbport = int(os.environ.get('DBPORT', '27017'))
_amqport = int(os.environ.get('AMQPORT', '5672'))
_mongod = os.environ.get('MONGOD', 'mongod')
_debug = os.environ.get('DEBUG', False)

CELERY_DISABLE_RATE_LIMITS = True
CELERY_RESULT_BACKEND = 'mongodb'
CELERY_MONGODB_BACKEND_SETTINGS = {
    'host': _host,
    'port': _dbport,
    'database': 'tasksdb',
    'taskmeta_collection': 'taskcoll',
}

CELERY_TIMEZONE = 'UTC'

BROKER_URL = "amqp://guest:guest@%s:%d" % (_host, _amqport)
BACKEND_URL = "mongodb://%s:%d" % (_host, _dbport)

ELERY_ACCEPT_CONTENT = ['json']

DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_RUNNER = 'main.tests.NoSQLTestRunner'

NOSE_ARGS = [
    '--nocapture',
    '--nologcapture'
]

mongoengine.connect('tmp', host=BACKEND_URL)

# MongoDB Databases
MONGODB_DATABASES = {
        'default': {'name': 'tmp'}
}

#DATABASES = {
#    'default': {}
#}
#SESSION_ENGINE = 'mongoengine.django.sessions'
#session = MongoSession.objects.get(pk=sessionkey)

DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_engine',
        'NAME' : 'tmp'
    }
}



AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# following these steps to get siteid when the db is updated
#python ./manage.py shell
#
#>>> from django.contrib.sites.models import Site
#>>> s = Site()
#>>> s.save()
#python ./manage.py tellsiteid
SITE_ID=u'54747c5a1fd21ca8c89fd773'
#SITE_ID=1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = root('collected_static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'


STATICFILES_DIRS = [os.path.join('./', 'static')]
## Additional locations of static files
#STATICFILES_DIRS = (
#    root('static')
#    # Put strings here, like "/home/html/static" or "C:/www/django/static".
#    # Always use forward slashes, even on Windows.
#    # Don't forget to use absolute paths, not relative paths.
#)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
)

COMPRESS_JS_FILTERS = [
        'compressor.filters.template.TemplateFilter',
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x2$s&amp;0z2xehpnt_99i8q3)4)t*5q@+n(+6jrqz4@rt%a8fdf+!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'main.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'main.wsgi.application'

TEMPLATE_DIRS = (
    root('templates')
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

COMPRESS_ENABLED = True

INSTALLED_APPS = (
    'django_nose',
    'django_mongodb_engine',
    'django.contrib.auth',
    'mongoengine.django.mongo_auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    #'kombu.transport.django.KombuAppConfig',
    'compressor',
    'bin',
    'handler',
    'algorithm'
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

AUTH_USER_MODEL = ('mongo_auth.MongoUser')
MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# used to schedule tasks periodically and passing optional arguments
# Can be very useful. Celery does not seem to support scheduled task
# but only periodic
CELERYBEAT_SCHEDULE = {
    'run_scrapy_service_twseid': {
        'task': 'bin.tasks.run_scrapy_service',
        'schedule': crontab(minute=0, hour='*/8'),
        'args': (
            'twseid',
            'INFO',
            "./log/%s_%s.log" % ('twseid', datetime.today().strftime("%Y%m%d_%H%M")),
            True,
            _debug
        )
    },
    'run_scrapy_service_otcid': {
        'task': 'bin.tasks.run_scrapy_service',
        'schedule': crontab(minute=0, hour='*/8'),
        'args': (
            'otcid',
            'INFO',
            "./log/%s_%s.log" % ('otcid', datetime.today().strftime("%Y%m%d_%H%M")),
            True,
            _debug
        )
    },
    'run_scrapy_service_twsehistrader': {
        'task': 'bin.tasks.run_scrapy_service',
        'schedule': crontab(minute=40, hour='*/8'),
        'args': (
            'twsehistrader',
            'INFO',
            "./log/%s_%s.log" % ('twsehistrader', datetime.today().strftime("%Y%m%d_%H%M")),
            True,
            _debug
        )
    },
    'run_scrapy_service_twsehisstock': {
        'task': 'bin.tasks.run_scrapy_service',
        'schedule': crontab(minute=40, hour='*/8'),
        'args': (
            'twsehisstock',
            'INFO',
            "./log/%s_%s.log" % ('twsehisstock', datetime.today().strftime("%Y%m%d_%H%M")),
            True,
            _debug
        )
    },
    'run_scrapy_service_otchistrader': {
        'task': 'bin.tasks.run_scrapy_service',
        'schedule': crontab(minute=40, hour='*/8'),
        'args': (
            'otchistrader',
            'INFO',
            "./log/%s_%s.log" % ('otchistrader', datetime.today().strftime("%Y%m%d_%H%M")),
            True,
            _debug
        )
    },
    'run_scrapy_service_otchisstock': {
        'task': 'bin.tasks.run_scrapy_service',
        'schedule': crontab(minute=40, hour='*/8'),
        'args': (
            'otchisstock',
            'INFO',
            "./log/%s_%s.log" % ('otchisstock', datetime.today().strftime("%Y%m%d_%H%M")),
            True,
            _debug
        )
    }
}
