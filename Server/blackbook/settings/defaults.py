import os
here = lambda * x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

PROJECT_ROOT = here('..')

root = lambda * x: os.path.join(os.path.abspath(PROJECT_ROOT), *x)

PROJECT_MODULE = '.'.join(__name__.split('.')[:-2])  # cut .settings.base

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

MEDIA_ROOT = root('static', 'uploads')
MEDIA_URL = '/static/uploads/'

STATIC_ROOT = root('static', 'assets')
STATIC_URL = '/static/assets/'

ADMIN_MEDIA_PREFIX = '/static/assets/admin/'

STATICFILES_DIRS = (
    root('staticfiles'),
)

ROOT_URLCONF = '%s.settings.urls' % PROJECT_MODULE

TEMPLATE_DIRS = (
    root('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.gis',
    #'staticfiles',

    # external
    #'south',
    'piston',
    'geopy',

    # internal
    'iconography',
)

SITE_ID = 1

TEST_EXCLUDE = ('django',)
TEST_RUNNER = '%s.settings.test_suite.AdvancedTestSuiteRunner' % PROJECT_MODULE


