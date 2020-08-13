from django.test import TestCase
from django.core.mail import send_mail
import os
import redis
from django.contrib.auth.models import User
from account.models import UserInfo
from django.urls import reverse


class AccountTest(TestCase):
    @staticmethod
    def connet_redis():
        r = redis.StrictRedis(host="localhost", port=6379, db=0)
        return r

    def test_get_code4(self):
        """
        测试获取注册用的验证码
        """
        response = self.client.get('/account/sendemail/?email=11@qq.com')
        code4 = self.connet_redis().get("11@qq.com")
        self.assertEqual(len(code4), 4, "验证码无法存入redis中")
        self.assertEqual(response.status_code, 200, "无法发送验证码")

    def test_send_mail(self):
        """
        测试发送邮件功能
        """
        result = send_mail(
            '来自李扣在线评测系统的邮件',
            "您的验证码为:",
            os.environ.get("EMAIL_HOST_USER"),
            ("11@qq.com",),
        )
        self.assertEqual(result, 1, "发送邮件失败")

    def save_auth(self):
        """
        创建一个用户
        """
        user = User.objects.create_user("sundy", "sundy@qq.com", "123")
        user.save()

    def login(self):
        """
        登陆
        """
        self.client.post(reverse('account:login'),
                         {'user_name': 'sundy', 'user_password1': '123'},
                         follow=True)

    def test_class_record(self):
        """
        测试查看：
            上课记录页面
            用户笔记页面
            提交代码的页面
        """
        self.save_auth()
        self.login()
        response = self.client.get(reverse('account:classrecode'))
        self.assertEqual(response.status_code, 200, "上课记录页面有误")

        response = self.client.get(reverse('account:show_user_notes'))
        self.assertEqual(response.status_code, 200, "查看用户笔记页面有误")

        response = self.client.get(reverse('account:submit_record'))
        self.assertEqual(response.status_code, 200, "查看用户提交的代码列表页面有误")



