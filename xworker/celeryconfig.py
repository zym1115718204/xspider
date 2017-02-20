BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_ENABLE_UTC = True

# CELERY_ROUTES = {
#          'tasks.add': 'low-priority',
#  
#  }
 
CELERY_ANNOTATIONS = {
        'tasks.add': {'rate_limit': '10/m'},
        'xworker.tasks.add': {'rate_limit': '10/m'},
        'xworker.task1.enterprise': {'rate_limit': '10/m'}

}

CELERY_IMPORTS = (                                  
                      'xworker.tasks',
                      'xworker.task1'
                  )
