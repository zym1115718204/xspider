"""
Django settings for xspider project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from common import *


# Spiders Path
PROJECTS_PTAH = os.path.join(os.path.dirname(BASE_DIR), "projects")

# Execute Path
EXECUTE_PATH = os.path.join(BASE_DIR, "execute")

# Redis Settings
REDIS_URL = 'localhost:6379'

# Mongodb settings
MongoDBS = {
    'xspider_project': {
        'host': 'mongodb://localhost/xspider_project',
    },
    'xspider_task': {
        'host': 'mongodb://localhost/xspider_task',
    },
    'xspider_result': {
        'host': 'mongodb://localhost/xspider_result',
    }
}

from mongoengine import connect  # noqa

for name, db in MongoDBS.iteritems():
    connect(host=db['host'], alias=name)


# Celery settings

BROKER_URL = 'amqp://guest:guest@localhost//'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)

# BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_ENABLE_UTC = True

CELERY_ROUTES = {
         'xspider.celery.debug_task': 'test',
         'xspider.celery.low_generator': 'low-generator',
         'xspider.celery.high_generator': 'high-generator',
         'xspider.celery.mid_generator': 'mid-generator',
         'xspider.celery.low_processor': 'low-processor',
         'xspider.celery.mid_processor': 'mid-processor',
         'xspider.celery.high_processor': 'high-processor',
 }

CELERY_ANNOTATIONS = {
    'xspider.celery.low_generator': {'rate_limit': '60/m'},
    'xspider.celery.high_generator': {'rate_limit': '60/m'},
    'xspider.celery.mid_generator': {'rate_limit': '60/m'},
    'xspider.celery.low_processor': {'rate_limit': '60/m'},
    'xspider.celery.high_processor': {'rate_limit': '60/m'},
    'xspider.celery.mid_processor': {'rate_limit': '60/m'},
    'xspider.celery.debug_task': {'rate_limit': '60/m'},
}

CELERY_IMPORTS = (
    'xspider.celery',
)


