
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db',
    }
}

SECRET_KEY = 'NO_SECRET_KEY'

INSTALLED_APPS = ('djqscsv_tests',)

ROOT_URLCONF = 'djqscsv_tests.urls'

DEBUG = True
