from django.test import TestCase
from judger_problem.models import Problem
from django.contrib.auth.models import User
from account.models import UserInfo
from django.urls import reverse
import pdb


# Create your tests here.

class ProblemTest(TestCase):
    def save_auth(self):
        """
        创建一个用户
        :return:
        """
        user = User.objects.create_user("sundy", "sundy@qq.com", "123")
        user.save()
        UserInfo(user=user).save()

    def save_problem(self):
        """
        创建一个题目
        :return:
        """
        problem = Problem()
        problem.title = "入门测试题目"
        problem.problem_content = "xxxxx"
        problem.problem_input = "1 2"
        problem.problem_output = "3"
        problem.problem_test_case_input = "1 2///3 4///"
        problem.problem_test_case_output = "3///7///"
        problem.fk_author = User.objects.get()
        problem.save()

    def test_save_problem(self):
        """
        测试保存题目功能
        :return:
        """
        self.save_auth()
        self.save_problem()
        self.assertEqual(Problem.objects.get().title, "入门测试题目", "题目保存失败")

    def login(self):
        """
        登陆
        :return:
        """
        self.client.post(reverse('account:login'),
                         {'user_name': 'sundy', 'user_password1': '123'},
                         follow=True)

    def test_submit_code(self):
        """
        测试提交代码
        :return:
        """
        self.save_auth()
        self.save_problem()
        self.login()
        self.assertEqual(Problem.objects.first().Submits, 0, "代码提交总数初始值应该为0")
        file = open("judger_problem/tests/a_b.cpp", 'r')
        response = self.client.post(
            reverse('problem:problemdetail', args=[Problem.objects.first().id]),
            {'user_code': file.read()}, follow=True)
        self.assertEqual(Problem.objects.first().Submits, 1, "提交代码时候，代码提交总数没变")
        self.assertEqual(
            len(User.objects.first().user_info.right_problems.all()), 1,
            "用户信息表中正确题目没变")

        print(response)
