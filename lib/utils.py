from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django_redis import get_redis_connection


def check_captcha(uuid, captcha):
    """
    检测图形验证码是否正确
    :param uuid: 唯一id
    :param captcha: 需要校验的验证码
    :return: True验证码正确 False验证码错误
    """
    try:
        redis_conn = get_redis_connection('verify_captcha')
        correct_captcha = redis_conn.get("image_uuid:{}".format(uuid))
    except Exception as e:
        print("连接redis失败{}".format(e))
        return False
    if (correct_captcha is None) or (
            correct_captcha.decode().lower() != captcha.lower()):
        return False
    else:
        return True


class JsonResponseSimple(JsonResponse):
    """
    重写JsonResponse
    简便返回json
    """
    def __init__(self, show, msg, encoder=DjangoJSONEncoder, safe=True,
                 json_dumps_params=None, **kwargs):
        data = {"show": show, "msg": msg}
        super().__init__(data, encoder, safe, json_dumps_params, **kwargs)
