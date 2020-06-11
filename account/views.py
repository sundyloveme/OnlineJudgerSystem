import random
import functools
import os

from django.shortcuts import render
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator

from judger_problem.models import SubmitStatus, Notes
from account.models import ClassRecode


@method_decorator(login_required, name="dispatch")
class ClassRecodeView(View):
    """
    上课记录视图
    """

    def get(self, request, *args, **kwargs):
        if "class_recode_id" in request.GET:
            """如果存在class_recode_id查询参数，渲染讲师评语页面"""
            context = {"class_recode": ClassRecode.objects.filter(id=request.GET['class_recode_id'])[0]}
            return render(request, template_name="account/templates/comment_detail.html", context=context)
        else:
            """不存在class_recode_id查询参数，渲染上课记录列表"""
            context = {'class_recode_list': ClassRecode.objects.filter(fk_user=self.request.user)}
            return render(request, template_name="account/templates/class_recode_list.html", context=context)


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, template_name="account/templates/login.html", context={})

    def post(self, request, *args, **kwargs):
        username = request.POST['user_name']
        password = request.POST['user_password1']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('problem:problemList'))
        else:
            return HttpResponse("登陆失败")


def logoutView(request):
    if request.method == "GET":
        logout(request)
        return HttpResponseRedirect(reverse('problem:problemList'))


class RegisterView(View):
    """
    用户注册的视图类
    """

    code4 = None

    def get(self, request, *args, **kwargs):
        return render(request, template_name="account/templates/register.html", context={})

    def post(self, request, *args, **kwargs):
        if request.POST['code4'] == self.code4:
            username = request.POST['user_name']
            useremail = request.POST['user_mail']
            password = request.POST['user_password1']
            password2 = request.POST['user_password2']
            if password2 != password:
                return HttpResponse('错误：两次密码不一致')
            user = User.objects.create_user(username=username, email=useremail, password=password)
            user.save()
            return HttpResponseRedirect(reverse('account:login'))


def sendEmailView(request):
    """
    发送邮件视图
    :param request:
    :return:
    """
    # 生成四位验证码
    num = functools.partial(random.randint, a=0, b=9)
    code4 = str(num()) + str(num()) + str(num()) + str(num())

    if request.method == "GET":
        send_mail(
            '来自李扣在线评测系统的邮件',
            "您的验证码为:" + code4,
            os.environ.get("EMAIL_HOST_USER"),
            [request.GET['email']],
        )
        RegisterView.code4 = code4
    return HttpResponse("验证码已发送至你的邮箱!")


@login_required
def submit_status_list_view(request):
    """
    查看提交状态
    :param request:
    :return:
    """
    if request.method == "GET":
        submit_list = SubmitStatus.objects.filter(author=request.user)
        context = {
            "submit_list": submit_list
        }
        return render(request, template_name="account/templates/submit_list.html", context=context)


@login_required
def note_list(request):
    """
    展示用户笔记列表
    :param request:
    :return:
    """
    if request.method == "GET":
        note_lists = Notes.objects.filter(author_id=request.user.id)
        context = {
            "note_list": note_lists,
        }
        return render(request, template_name="account/templates/note_list.html", context=context)


@login_required
def show_user_submited_code(request):
    """
    展示用户提交的代码
    :param request:
    :return:
    """
    if request.method == "GET":
        submit_id = request.GET['id']
        submit = SubmitStatus.objects.filter(id=submit_id)[0]
        context = {
            "user_code": submit.user_code_content
        }
        return render(request, template_name="account/templates/show_user_submited_code.html", context=context)
