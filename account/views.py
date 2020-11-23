import random
import functools
import os
import re

from django.shortcuts import render
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
import redis
from django_redis import get_redis_connection

from judger_problem.models import SubmitStatus, Notes
from account.models import ClassRecode, UserInfo
from online_judge_server.settings.base import connet_redis
from lib.captcha.captcha import captcha

from django.contrib.auth.models import AnonymousUser


@method_decorator(login_required, name="dispatch")
class ClassRecodeView(View):
    """
    上课记录视图
    """

    def get(self, request, *args, **kwargs):
        if "class_recode_id" in request.GET:
            """如果存在class_recode_id查询参数，渲染讲师评语页面"""
            class_recode = \
                ClassRecode.objects.filter(id=request.GET['class_recode_id'])[0]

            comments = class_recode.comment
            context = {"comments": comments}
            return render(request,
                          template_name="account/templates/comment_detail.html",
                          context=context)
        else:
            """不存在class_recode_id查询参数，渲染上课记录列表"""
            if request.user.is_staff:
                """如果是管理员登陆则显示所有人员上课记录"""
                context = {'class_recode_list': ClassRecode.objects.all()}
            else:
                context = {'class_recode_list': ClassRecode.objects.filter(
                    fk_user=self.request.user)}
            return render(request,
                          template_name="account/templates/class_recode_list.html",
                          context=context)


class LoginView(View):
    """
    登陆页面视图
    """

    def get(self, request, *args, **kwargs):
        if request.user == AnonymousUser():
            # 匿名用户展示登陆页面
            return render(request, template_name="account/templates/login.html",
                          context={})
        else:
            # 已登录用户不展示登陆页面
            return HttpResponseRedirect(reverse('problem:problemList'))

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


def check_email_repeat(request):
    """
    检测邮箱是否重复的接口
    :param request:
    :return:
    """
    if not request.method == 'POST':
        return HttpResponse("请使用post方式访问")
    else:
        if request.POST.get('email') == None:
            return HttpResponse("参数不齐")

        user_email = request.POST.get('email')

        if not re.match(
                "^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$",
                user_email):
            return JsonResponse({"show": 'true', "msg": "邮箱格式不合符规范"})

        if len(User.objects.filter(email=user_email)) > 0:
            return JsonResponse({"show": 'true', "msg": "该邮箱已注册"})

        return JsonResponse({"show": 'false', "msg": ""})


def check_nick_name_repeat(request):
    """
    检测昵称是否重复
    :param request:
    :return:
    """
    if not request.method == 'POST':
        return HttpResponse("请使用post方式访问")
    else:
        if request.POST.get('nick_name') == None:
            return HttpResponse("参数不齐")

        nick_name = request.POST.get('nick_name')

        if not re.match("^[a-zA-Z0-9_\u4e00-\u9fa5]+$", nick_name):
            return JsonResponse({"show": 'true', "msg": "用户名不符合规范"})

        if len(User.objects.filter(username=nick_name)) > 0:
            return JsonResponse({"show": 'true', "msg": "该用户名已注册"})

        return JsonResponse({"show": 'false', "msg": ""})


def get_captcha(request):
    """
    获取验证码接口
    get方式提供uuid 验证码和uuid绑定
    :param request:
    :return:
    """
    if not request.method == 'GET':
        return HttpResponse("请使用get方式访问")
    else:
        if request.GET.get('uuid') == None:
            return HttpResponse("参数不齐")
        uuid = request.GET.get('uuid')

        try:
            text, image = captcha.generate_captcha()
        except Exception as e:
            print("生成图形验证码失败 {}".format(e))

        try:
            redis_conn = get_redis_connection('verify_captcha')
        except Exception as e:
            print("连接redis数据库失败 {}".format(e))

        redis_conn.setex("image_uuid:{}".format(uuid), 60 * 5,
                         text)  # 验证码保存在redis中三分钟
        print("image_uuid:{} = {}".format(uuid, text))
        return HttpResponse(content_type='image/jpg', content=image)


def check_captcha(request):
    """
    验证码是否正确接口
    get方式提供 uuid和验证码
    :param request:
    :return:
    """
    if request.method == "GET":
        uuid = request.GET.get('uuid')
        captcha_code = request.GET.get('captcha_code')
        if not all([uuid, captcha_code]):
            return HttpResponse("参数不齐全")

        try:
            redis_conn = get_redis_connection('verify_captcha')
        except Exception as e:
            print("redis连接异常 {}".format(e))
        correct_code = redis_conn.get("image_uuid:{}".format(uuid))
        print("correct_code is {}".format(correct_code))
        if correct_code.decode().lower() == captcha_code.lower():
            return JsonResponse({"show": "false", "msg": ""})
        else:
            return JsonResponse({"show": "true", "msg": "验证码错误"})


class RegisterView(View):
    """
    用户注册的视图类
    """

    def get(self, request, *args, **kwargs):
        return render(request, template_name="account/templates/register.html",
                      context={})

    def post(self, request, *args, **kwargs):
        if len(User.objects.filter(email=request.POST['user_mail'])) > 0:
            return HttpResponse("您输入的邮箱已经注册")

        if len(User.objects.filter(username=request.POST['user_name'])) > 0:
            return HttpResponse("您输入的昵称已经注册")

        if len(request.POST['code4']) < 4:
            return HttpResponse("请输入验证码")

        # 用户输入的四位验证码和redis数据库中的四位验证码
        if request.POST['code4'] == connet_redis().get(
                request.POST['user_mail']).decode("utf-8"):
            username = request.POST['user_name']
            useremail = request.POST['user_mail']
            password = request.POST['user_password1']
            password2 = request.POST['user_password2']
            if password2 != password:
                return HttpResponse('错误：两次密码不一致')
            user = User.objects.create_user(username=username, email=useremail,
                                            password=password)
            UserInfo(user=user).save()
            user.save()
            return HttpResponseRedirect(reverse('account:login'))
        else:
            return HttpResponse("您输入的验证码有误")


def sendEmailView(request):
    """
    发送邮件视图
    :param request:request.GET['email']用户邮箱
    :return:
    """

    if len(User.objects.filter(email=request.GET['email'])) > 0:
        return HttpResponse("您输入的邮箱已经注册")

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

    # 四位验证码存入redis数据库
    # 如 key=xxx@mail.com, value="1234"
    r = connet_redis()
    r.set(request.GET['email'], code4)
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
        return render(request,
                      template_name="account/templates/submit_list.html",
                      context=context)


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
        return render(request, template_name="account/templates/note_list.html",
                      context=context)


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
        return render(request,
                      template_name="account/templates/show_user_submited_code.html",
                      context=context)
