import redis

# redis配置
r = redis.StrictRedis(host="localhost", port=6379, db=0)


def connet_redis():
    return r
