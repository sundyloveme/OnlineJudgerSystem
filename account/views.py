import functools
import logging
import os
import random
import re
import time

from django import conf
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from minio import Minio

from account.models import UserInfo
from celery_tasks import tasks
from judger_problem.models import SubmitStatus
from lib import utils, re_express
from lib.captcha.captcha import captcha
from lib.utils import JsonResponseSimple
from online_judge_server.settings.base import connet_redis

logger = logging.getLogger('django')


def check_name_passwd_cap(POST):
    """
    检测用户名、密码和验证码是否正确
    :param POST: 字典，包含用户名、密码和验证码
    :return:  正确 {"is_ok": True, "msg": ""}
    """

    result = {"is_ok": False, "msg": ""}

    try:
        username = POST.get('user_name')[0]
        password = POST.get('user_password1')[0]
        captcha = POST.get('captcha')[0]
        uuid = POST.get('uuid')[0]
    except Exception as e:
        logger.error('参数获取失败 {}'.format(e))
        raise e

    if not all([username, password, captcha, uuid]):
        result['msg'] = "信息不全"
        return result

    # 检测验证码是否正确
    if not utils.check_captcha(uuid, captcha):
        result['msg'] = "验证码错误"
        return result

    # 检测用户名和密码
    if re.match(re_express.email_express, username):
        # 邮箱
        user = User.objects.filter(email=username)
        if (len(user)) <= 0 or (user[0].check_password(password) != True):
            result['msg'] = "用户名或者密码错误"
            return result
    else:
        # 用户名
        user = authenticate(username=username, password=password)
        if user is None:
            result['msg'] = "用户名或者密码错误"
            return result

    result['is_ok'] = True
    return result


class CheckLoginView(View):
    def post(self, request):
        """
        视图类
        检测用户用户信息是否正确
        :param request: request.POST包含用户信息
        :return: Json格式。 正确show="false"， 错误show="true"
        """
        POST = dict(request.POST)
        result = check_name_passwd_cap(POST)
        if result['is_ok']:
            return JsonResponseSimple(show="false", msg='')
        else:
            return JsonResponseSimple(show="true", msg=result['msg'])


class LoginView(View):
    """
    登陆页面视图
    """

    def get(self, request, *args, **kwargs):
        """
        渲染登陆页面
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if request.user == AnonymousUser():
            # 匿名用户展示登陆页面
            return render(request, template_name="account/templates/login.html",
                          context={})
        else:
            # 已登录用户不展示登陆页面
            return HttpResponseRedirect(reverse('problem:problemList'))

    def post(self, request):
        """
        用户登陆
        :param request: request.POST包含用户信息
        :return: 登陆成功返回首页，失败返回失败信息
        """
        POST = dict(request.POST)
        # 验证用户名、密码、验证码正确性
        result = check_name_passwd_cap(POST)
        if result['is_ok']:
            username = POST.get('user_name')[0]
            # 检测用户名和密码
            if re.match(re_express.email_express, username):
                # 邮箱登陆
                user = User.objects.filter(email=username)[0]
            else:
                # 用户名登陆
                user = User.objects.filter(username=username)[0]
            login(request, user)
            return HttpResponseRedirect(reverse('problem:problemList'))
        else:
            return HttpResponse("登陆失败")


def logoutView(request):
    """
    用户退出登陆视图
    释放session数据
    :param request:
    :return:
    """
    if request.method == "GET":
        logout(request)
        return HttpResponseRedirect(reverse('problem:problemList'))


def check_email_repeat(request):
    """
    检测邮箱是否重复的接口
    :param request: POST['email']
    :return: 重复:show="true"
    """
    if not request.method == 'POST':
        return JsonResponseSimple(show="true", msg='请使用post方式访问')
    else:
        if request.POST.get('email') == None:
            return JsonResponseSimple(show="true", msg='参数不齐')

        user_email = request.POST.get('email')

        if not re.match(re_express.email_express, user_email):
            return JsonResponseSimple(show="true", msg='邮箱格式不合符规范')

        if len(User.objects.filter(email=user_email)) > 0:
            return JsonResponseSimple(msg="该邮箱已注册", show="true")

        return JsonResponseSimple(msg="", show='false')


def check_nick_name_repeat(request):
    """
    检测昵称是否重复
    :param request:
    :return:
    """

    if not request.method == 'POST':
        return JsonResponseSimple(show='true', msg="请使用post方式访问")
    else:
        if request.POST.get('nick_name') == None:
            return JsonResponseSimple(show='true', msg="参数不齐")

        nick_name = request.POST.get('nick_name')

        if not re.match(re_express.nick_name_express, nick_name):
            return JsonResponseSimple(show='true', msg="用户名不符合规范")

        if len(User.objects.filter(username=nick_name)) > 0:
            return JsonResponseSimple(show='true', msg="该用户名已注册")
        return JsonResponseSimple(show='false', msg="")


def get_captcha(request):
    """
    获取验证码接口
    get方式提供uuid
    return 图形验证码
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
    检测图形验证码是否正确接口
    get方式提供: uuid和验证码
    """
    if request.method == "GET":
        uuid = request.GET.get('uuid')
        captcha_code = request.GET.get('captcha_code')
        if not all([uuid, captcha_code]):
            return JsonResponseSimple(show='true', msg="参数不齐全")

        if utils.check_captcha(uuid, captcha_code):
            return JsonResponseSimple(show='false', msg="")
        else:
            return JsonResponseSimple(show='true', msg="验证码错误")


class RegisterView(View):
    """
    用户注册的视图类
    """

    def get(self, request, *args, **kwargs):
        return render(request, template_name="account/templates/register.html",
                      context={})

    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        user_mail = request.POST.get('user_mail')
        user_name = request.POST.get('user_name')
        user_password1 = request.POST.get('user_password1')
        user_password2 = request.POST.get('user_password2')
        captcha = request.POST.get('captcha')
        uuid = request.POST.get('uuid')

        # 参数齐全检测
        if not all(
                [user_mail, user_name, user_password1, user_password2, captcha,
                 uuid]):
            return JsonResponse({"show": "true", "msg": "请正确填写"})

        # 邮箱重复检测
        if not re.match(re_express.email_express, user_mail):
            return JsonResponse({"show": 'true', "msg": "邮箱格式不合符规范"})
        if len(User.objects.filter(email=user_mail)) > 0:
            return JsonResponse({"show": 'true', "msg": "该邮箱已注册"})

        # 用户名重复检测
        if not re.match(re_express.nick_name_express, user_name):
            return JsonResponse({"show": 'true', "msg": "用户名不符合规范"})
        if len(User.objects.filter(username=user_name)) > 0:
            return JsonResponse({"show": 'true', "msg": "该用户名已注册"})

        # 验证码检测
        if not utils.check_captcha(uuid, captcha):
            return JsonResponse({"show": "true", "msg": "验证码错误"})

        # 密码两次一样检测
        if user_password1 != user_password2:
            return JsonResponse({"show": "true", "msg": "两次密码不一样"})

        # 保存用户信息
        user = User.objects.create_user(username=user_name, email=user_mail,
                                        password=user_password1)
        UserInfo(user=user).save()
        login(request, user)
        return HttpResponseRedirect(reverse('problem:problemList'))


# def sendEmailView(request):
#     """
#     发送邮件视图
#     :param request:request.GET['email']用户邮箱
#     :return:
#     """
#
#     if len(User.objects.filter(email=request.GET['email'])) > 0:
#         return HttpResponse("您输入的邮箱已经注册")
#
#     # 生成四位验证码
#     num = functools.partial(random.randint, a=0, b=9)
#     code4 = str(num()) + str(num()) + str(num()) + str(num())
#
#     if request.method == "GET":
#         send_mail(
#             '来自李扣在线评测系统的邮件',
#             "您的验证码为:" + code4,
#             os.environ.get("EMAIL_HOST_USER"),
#             [request.GET['email']],
#         )
#
#     # 四位验证码存入redis数据库
#     # 如 key=xxx@mail.com, value="1234"
#     r = connet_redis()
#     r.set(request.GET['email'], code4)
#     return HttpResponse("验证码已发送至你的邮箱!")


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


def submit_status_all_list_view(request):
    """
    查看所有人的提交状态提交状态
    :param request:
    :return:
    """
    if request.method == "GET":
        submit_list = SubmitStatus.objects.all()
        context = {
            "submit_list": submit_list
        }
        return render(request,
                      template_name="account/templates/submit_list.html",
                      context=context)


# @login_required
# def note_list(request):
#     """
#     展示用户笔记列表
#     :param request:
#     :return:
#     """
#     if request.method == "GET":
#         note_lists = Notes.objects.filter(author_id=request.user.id)
#         context = {
#             "note_list": note_lists,
#         }
#         return render(request, template_name="account/templates/note_list.html",
#                       context=context)


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


def load_file(request):
    """
    上传文件接口
    :param request:
    :return:
    """

    minio_host_url = conf.settings.MINIO_URL
    if request.method == "GET":
        return render(request,
                      template_name='account/templates/upload_file.html')

    if request.method == "POST":
        file = request.FILES.get('file')
        if file is None:
            return JsonResponseSimple(show='false', msg='')

        # 提取图片类型
        try:
            type_name = file.name.split(".")[-1]
        except:
            return JsonResponseSimple(show='true', msg='提取文件名失败')

        # 随机化名字 time+随机值
        try:
            object_name = time.time().__str__().replace('.', '_') \
                          + "_" \
                          + random.random().__str__().replace('.', "_") \
                          + "." \
                          + type_name
        except:
            return JsonResponseSimple(show='true', msg='拼接文件名错误')

        # 上传文件
        try:
            minioClient = Minio(endpoint=minio_host_url,
                                access_key='minioadmin',
                                secret_key='minioadmin',
                                secure=False)
            obj = minioClient.put_object("images", object_name, file,
                                         file.size, content_type='image/png')
        except Exception as e:
            return JsonResponseSimple(show='true',
                                      msg="文件上传至 minio出错{}".format(e))

        return JsonResponse(
            {"msg": 'http://' + minio_host_url + '/' + 'images/' + object_name})
    else:
        return JsonResponseSimple(show='true', msg="类型错误，请使用post")


def send_email_captcha(request):
    """
    发送邮箱验证码
    :param request:
    :return:
    """
    if request.method == 'GET':
        email = request.GET.get('email')
        if email is None:
            return HttpResponse("邮箱不能为空")

        if not re.match(
                re_express.email_express,
                email):
            return HttpResponse("邮箱格式不正确")

        try:
            text, image = captcha.generate_captcha()
        except:
            print("生成验证码失败")

        print("{} -> 验证码是{}".format(email, text))

        redis_conn = get_redis_connection('verify_captcha')
        redis_conn.setex('email_captcha:{}'.format(email), 60 * 5, text)
        tasks.send_email.delay(email, '邮箱验证', '您的验证码是{}'.format(text))
        return HttpResponse("邮件发送成功")
    else:
        return HttpResponse("请使用get方法访问")


class VerifyEmail(View):
    def post(self, request):
        """
        验证邮箱验证码
        :return:
        """
        email = request.POST.get("email")
        captcha = request.POST.get("captcha")

        if not all([email, captcha]):
            return HttpResponse("参数不齐全")

        redis_conn = get_redis_connection('verify_captcha')

        try:
            correct_captcha = redis_conn.get('email_captcha:{}'.format(email))
        except:
            return HttpResponse("验证码错误")
        if correct_captcha == None:
            return HttpResponse("验证码错误")

        if correct_captcha.decode().lower() == captcha.lower():
            return HttpResponse("邮箱校验成功")
        else:
            return HttpResponse("验证码错误")


class Profile(View):
    def get(self, request, big_message=""):
        """
        渲染用户信息页面
        :param request:
        :return:
        """
        if request.user.is_anonymous:
            # 未登录跳转到登陆页面
            return HttpResponseRedirect(reverse('account:login'))

        try:
            # 没有user_info 信息 新建一个
            user_info = request.user.user_info
        except:
            userinfo = UserInfo(user=request.user)
            request.user.user_info = userinfo
            userinfo.save()
            request.user.save()

        nick_name = request.user.username
        phone = request.user.user_info.iphone
        email = request.user.email
        resume = request.user.user_info.info

        context = {
            "nick_name": nick_name,
            "phone": phone,
            'email': email,
            'resume': resume,
            'big_message': big_message,
        }

        return render(request, template_name='account/templates/profile.html',
                      context=context)

    def post(self, request):
        """
        提交新的用户信息
        :param request:
        :return:
        """
        if request.user.is_anonymous:
            # 未登录跳转到登陆页面
            return HttpResponseRedirect(reverse('account:login'))

        try:
            # 校验邮箱验证码是否正确
            result = VerifyEmail().post(request).content.decode()
            if result != '邮箱校验成功':
                return self.get(request, result)
        except Exception as e:
            logger.info("校验邮箱验证码失败{}".format(e))

        nick_name = request.POST.get('nick_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        resume = request.POST.get('resume')

        # if not all([nick_name, phone, email]):
        #     return self.get(request, big_message='信息不全')

        request.user.username = nick_name
        request.user.user_info.iphone = phone
        request.user.email = email
        request.user.user_info.info = resume

        request.user.save()
        request.user.user_info.save()

        return self.get(request)
