from .dev import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'online_judge_server_database',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': "db",
        'PORT': 3306,
        'OPTIONS': {
            'sql_mode': 'traditional',
        }
    }
}
