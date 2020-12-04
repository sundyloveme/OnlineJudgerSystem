import json
import logging

import markdown2
import requests
from django import conf
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from haystack.views import SearchView

from .models import Problem, SubmitStatus, ProblemLabel, Notes

logger = logging.getLogger("django")


def search_problem_view(request):
    proble_list_all = Problem.get_sth_problem_list(request.POST['keyword'])

    # 分页
    pagetor = Paginator(proble_list_all, 10)
    page = request.GET.get('page') if request.GET.get(
        'page') is not None else 1
    proble_lists = pagetor.get_page(page)

    context = {
        "proble_lists": proble_lists,
    }
    return render(request,
                  template_name="judger_problem/templates/problem_search_list.html",
                  context=context)


class SearchJsonView(SearchView):
    """
    重写haystack的视图函数
    原本返回的是html模板，重写后返回json数据
    """

    def create_response(self):
        results = self.get_context()
        ret = []

        for result in results['page'].object_list:
            ret.append({"id": result.object.id,
                        "title": result.object.title})

        return JsonResponse(ret, safe=False)


def get_problem_counts():
    """
    查询题库中题目的总数
    :return: 题库中题目的总数
    """
    try:
        count = Problem.get_problem_list().count()
    except Exception as e:
        logger.error("查询错误 {}".format(e))
        raise e
    return count

def get_problem_counts_view(request):
    """
    视图函数
    json接口, 返回题库中题目的总数的接口视图
    :param request:
    :return: 总数
    """
    count = get_problem_counts()
    return JsonResponse(dict(count=count))


def get_user_correct_problem_counts(request):
    """
    查询用户正确的题目的总数
    需要确保当前用户已经登陆
    :param request: request.user 当前登录的用户对象
    :return: 正确的题目的总数
    """
    try:
        query = request.user.submit_status.filter(user_code_status='正确')
    except Exception as e:
        logger.error("查询用户正确题目出错")
        return 0
    return len(query)


def get_user_correct_problem_counts_view(request):
    """
    视图函数
    查询用户正确的题目的总数
    :param request: request.user 当前登录的用户对象
    :return: 正确的题目的总数
    """
    if request.user.is_authenticated is True:
        count = get_user_correct_problem_counts(request)
        return JsonResponse(dict(count=count))
    else:
        return JsonResponse(dict(msg="未登录，无法查询"))


def get_problem_labes_view(request):
    """
    视图函数
    获取所有题目标签
    :param request:
    :return: 以Json格式字符串返回标签列表
    """
    labels = ProblemLabel.objects.all().only('name')
    return JsonResponse(dict(labels=[lable.name for lable in labels]))


# @method_decorator(login_required, name="dispatch")
class ProblemList(View):
    """
    首页视图
    """

    # proble_list_all = Problem.get_problem_list()

    # def get_problem_count(self):
    #     """
    #     获取题目总数
    #     :return: 题目总数
    #     """
    #     try:
    #         return self.proble_list_all.count()
    #     except Exception as e:
    #         print("返回题目总数出错", e)
    #         return None

    def get_user_correct_problems_id(self, user):
        """
        用户正确题目id集合
        :param user: 被查询用户对象
        :return: user对象的正确题目的id集合 eg:{1, 3}
        """
        try:
            query = user.submit_status.filter(user_code_status='正确')
        except Exception as e:
            print("查询用户正确题目出错", e)
            return []
        query = set([q.fk_problem_id_id for q in query])
        return query

    def get_problem_label(self):
        """
        获得题目标签
        :return: 返回所有题目标签
        """
        labels = ProblemLabel.objects.all()
        return labels

    def get(self, request):
        """处理get请求"""

        # 已解决题目数量
        # solve_count = self.get_user_correct_problems_id(request.user).__len__()
        solve_count = get_user_correct_problem_counts(request)

        # 未解决题目数量
        unsolve_count = get_problem_counts() - solve_count

        # user对象的正确题目的id集合
        right_prolems = self.get_user_correct_problems_id(request.user)
        right_prolems = list(right_prolems)

        # 分页 每页10条
        pagetor = Paginator(Problem.objects.all().order_by('id'), 10)
        page = request.GET.get('page', 1)
        proble_lists = pagetor.get_page(page)

        context = {
            "right_prolems": right_prolems,
            "proble_lists": proble_lists,
            "unsolve_count": unsolve_count,
            "solve_count": solve_count,
            "labels": self.get_problem_label(),
        }
        return render(request,
                      template_name="judger_problem/templates/problem_list.html",
                      context=context)


@login_required
@csrf_exempt
def saveNote(request, problem_id):
    """
    处理保存笔记的视图
    :param request:
    :param problem_id:
    :return:
    """
    if request.method == "POST":
        note = Notes.objects.filter(fk_problem_id=problem_id,
                                    author_id=request.user.id)
        if len(note) != 0:
            note[0].content = request.POST['note_content']
            note[0].save()
        else:
            note = Notes()
            note.content = request.POST['note_content']
            note.author = request.user
            note.fk_problem = Problem.objects.filter(id=problem_id)[0]
            note.save()
        return HttpResponse("保存成功")


# @method_decorator(login_required, name="dispatch")
class ProblemDetail(View):
    """
    展示题目详情的视图
    """

    def get(self, request, *args, **kwargs):
        """
        处理get请求，返回题目详情页面
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        problem = Problem.objects.filter(id=kwargs["problem_id"])[0]
        # note = Notes.objects.filter(fk_problem_id=kwargs["problem_id"],
        #                             author_id=request.user.id).first()

        # markdown格式转为html格式
        problem_describes = markdown2.markdown(problem.problem_content)

        context = {
            "problem_describes": problem_describes,  # 题目描述
            "problem_content": problem,
            # "note": note,
            # "like_count": Problem.get_liked_conut(kwargs["problem_id"]),
            # "collect_count": Problem.get_collect_count(kwargs["problem_id"])
        }
        return render(request=request,
                      template_name="judger_problem/templates/problem_detail.html",
                      context=context)

    def get_user_outputs(self, user_code, test_case_inputs, url):
        """
        获取用户代码的运行结果
        :param user_code: 用户代码
        :param test_case_inputs: 输入测试用例列表
        :param url: 判题服务器地址
        :return: 如果代码运行错误，返回字符串"error"; 如果代码可以运行，返回代码运行结果输出列表。
        """
        # 用户代码运行输出结果列表
        user_test_case_outputs = []
        data = {
            "user_code": user_code.encode("utf-8"),
            "user_input": "",
        }
        for case_input in test_case_inputs:
            if case_input != "":
                data['user_input'] = case_input
                result = requests.post(url, data=data, timeout=10)
                result = json.loads(result.text)
                if result["status"] == "error":
                    return "error"
                user_test_case_outputs.append(result["output"])
        return user_test_case_outputs

    def is_correct_user_code(self, user_test_case_outputs, test_case_outputs):
        """
        判断用户输出结果是否正确
        :param user_test_case_outputs: 用户的输入
        :param test_case_outputs: 正确的输入
        :return: 正确返回True, 否则返回Flase
        """
        for i in range(0, len(user_test_case_outputs)):
            if user_test_case_outputs[i].replace("\n", "") != test_case_outputs[
                i]:
                return False
        return True

    def post(self, request, *args, **kwargs):
        """
        处理代码提交请求
        :param request: request.POST['user_code']包含用户代码
        :param kwargs: kwargs["problem_id"]提交的代码对应题号
        :return: 返回get请求同样的内容外，还返回用户代码提交结果信息mess,
                 以及status; error:表示用户代码无法运行, success:表示用户代码可以运行但是输出不一定正确
        """

        if request.user.is_authenticated == False:
            # 未登录 跳转到登陆页面
            return HttpResponseRedirect(reverse('account:login'))

        # 获取model对象problem
        problem = Problem.objects.filter(id=kwargs["problem_id"])[0]
        problem.Submits += 1
        problem.save()
        context = {
            "problem_content": problem,
            "mess": "",
        }

        # 向判题服务器发起post请求 运行代码
        user_code = request.POST['user_code']
        test_case_input_list = problem.problem_test_case_input.split("///")
        result = self.get_user_outputs(user_code, test_case_input_list,
                                       conf.settings.OJ_URL)
        # 设置提交状态
        submit_status = SubmitStatus()
        submit_status.fk_problem_id = problem
        submit_status.user_code_content = user_code
        submit_status.author = request.user

        # 用户代码不可以运行
        if result == "error":
            context["status"] = "error"
            context["mess"] = "代码无法运行"
            submit_status.user_code_status = "代码无法运行"
            submit_status.save()
            return render(request,
                          template_name="judger_problem/templates/problem_detail.html",
                          context=context)

        # 用户代码可运行，检测答案是否正确
        test_case_outputs = problem.problem_test_case_output.replace('\r\n',
                                                                     '')  # 去除测试用例输出的多余的换行
        test_case_outputs = test_case_outputs.split(
            "///")  # 测试用例输出转为列表 eg:[1, 2, 3]
        is_correct = self.is_correct_user_code(result, test_case_outputs)
        if is_correct:
            context["status"] = "success"
            context["mess"] = "答案正确"
            submit_status.user_code_status = "正确"
            problem.corrects += 1

            # 题目正确后添加入用户信息中的 "正确题目" 列表
            request.user.user_info.right_problems.add(problem)
            request.user.user_info.save()

            problem.save()
        else:
            context["status"] = "success"
            context["mess"] = "答案错误，请检查你的代码逻辑"
            submit_status.user_code_status = "错误"
        submit_status.save()
        return render(request,
                      template_name="judger_problem/templates/problem_detail.html",
                      context=context)
