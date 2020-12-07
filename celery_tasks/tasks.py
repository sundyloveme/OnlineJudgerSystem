if __name__ != '__main__':
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from celery import Celery
from send_email import send_email

app = Celery('tasks')
app.config_from_object('config')

send_email = app.task(send_email)


@app.task
def add(a, b):
    return a + b
