from django.test import TestCase
from judger_problem.models import Problem
from django.contrib.auth.models import User
from django.urls import reverse
import pdb


# Create your tests here.

class ProblemTest(TestCase):
    def save_auth(self):
        user = User()
        user.username = "sundy"
        user.password = "123"
        user.save()

    def save_problem(self):
        self.save_auth()
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
        self.save_problem()
        self.assertEqual(Problem.objects.get().title, "入门测试题目", "题目保存失败")

    def login(self):
        self.client.post(reverse('account:login'), {'user_name': 'sundy', 'user_password1': '123'}, follow=True)

    # def test_submit_code(self):
    #     self.login()
    #     file = open("judger_problem/tests/a_b.cpp", 'r')
    #     response = self.client.post(reverse('problem:problemdetail', args=[1]), {'user_code': file.read()})
    #     pdb.set_trace()
    #     print("")