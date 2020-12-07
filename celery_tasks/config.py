import os

broker_url = 'redis://' + os.environ.get("REDIS_HOST") + '/3'
result_backend = 'redis://' + os.environ.get("REDIS_HOST") + '/4'
