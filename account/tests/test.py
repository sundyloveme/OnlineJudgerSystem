from django.test import TestCase
from django.core.mail import send_mail
import os
import redis
from django.contrib.auth.models import User
from account.models import UserInfo


# Create your tests here.
# 测试能否发送验证码 存入redis

# 输入错误验证码

# 成功注册

class AccountTest(TestCase):
    @staticmethod
    def connet_redis():
        r = redis.StrictRedis(host="localhost", port=6379, db=0)
        return r

    def test_get_code4(self):
        """
        测试获取注册用的验证码
        :return:
        """
        response = self.client.get('/account/sendemail/?email=11@qq.com')
        code4 = self.connet_redis().get("11@qq.com")
        self.assertEqual(len(code4), 4, "验证码无法存入redis中")
        self.assertEqual(response.status_code, 200, "无法发送验证码")

    def test_send_mail(self):
        """
        测试发送邮件功能
        :return:
        """
        result = send_mail(
            '来自李扣在线评测系统的邮件',
            "您的验证码为:",
            os.environ.get("EMAIL_HOST_USER"),
            ("11@qq.com",),
        )
        self.assertEqual(result, 1, "发送邮件失败")

    def test_class_record(self):
        pass

    def test_user_problem_info(self):
        """

        :return:
        """
        john = User.objects.create_user("john", "john@ex.com", "123")
        john.save()
        # john.user_right
        UserInfo(user=john).save()
        john.user_info
        # self.assertEqual(john.user_recode, )
        # self.assertEqual(, )
