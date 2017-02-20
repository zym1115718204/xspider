from xworker import app

#app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')
#app.config_from_object('celeryconfig')

@app.task
def add(x, y):
    return x + y
