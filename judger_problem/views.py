import json

from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import requests
from django.shortcuts import HttpResponse

from .models import Problem, SubmitStatus, ProblemLabel, Notes


@method_decorator(login_required, name="dispatch")
class ProblemList(View):
    """
    题目列表视图
    """

    def get_problem_label(self):
        """
        获得题目标签
        :return:
        """
        labels = ProblemLabel.objects.all()
        return labels

    def get(self, request):
        proble_list_all = Problem.get_problem_list()

        # 已解决题目数量
        solve_count = len(SubmitStatus.objects.filter(user_code_status="正确", author=request.user))
        # 未解决题目数量
        problem_count = Problem.objects.count() - solve_count

        # 分页
        pagetor = Paginator(proble_list_all, 10)
        page = request.GET.get('page') if request.GET.get('page') is not None else 1
        proble_lists = pagetor.get_page(page)

        context = {
            "proble_lists": proble_lists,
            "problem_count": problem_count,
            "solve_count": solve_count,
            "labels": self.get_problem_label(),
        }
        return render(request, template_name="judger_problem/templates/problem_list.html", context=context)


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
        note = Notes.objects.filter(fk_problem_id=problem_id, author_id=request.user.id)
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


@method_decorator(login_required, name="dispatch")
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
        note = Notes.objects.filter(fk_problem_id=kwargs["problem_id"], author_id=request.user.id).first()

        context = {
            "problem_content": problem,
            "note": note,
            "like_count": Problem.get_liked_conut(kwargs["problem_id"]),
            "collect_count": Problem.get_collect_count(kwargs["problem_id"])
        }
        return render(request=request, template_name="judger_problem/templates/problem_detail.html", context=context)

    def post(self, request, *args, **kwargs):
        """
        处理代码提交请求
        :param request: request.POST['user_code']包含用户代码
        :param kwargs: kwargs["problem_id"]提交的代码对应题号
        :return: 返回get请求同样的内容外，还返回用户代码提交结果信息mess,
                 以及status; error:表示用户代码无法运行, success:表示用户代码可以运行但是输出不一定正确
        """

        # 获取model对象problem
        problem = Problem.objects.filter(id=kwargs["problem_id"])[0]
        context = {
            "problem_content": problem,
            "mess": "",
        }

        # 将用户代码和输入数据打包成data
        # 向判题服务器发起post请求
        # 将判题服务器结果转为json格式
        user_code = request.POST['user_code']
        data = {
            "user_code": user_code,
            "user_input": problem.problem_input,
        }

        # 设置提交状态
        submit_status = SubmitStatus()
        submit_status.fk_problem_id = problem
        submit_status.user_code_content = user_code
        submit_status.author = request.user

        # TODO ip地址应该写进环境变量中
        result = requests.post("http://120.92.173.80:8080/", data=data)
        # result = str(result, "utf-8")
        result = json.loads(result.text)

        # 用户代码不可以运行
        if result["status"] == "error":
            context["status"] = "error"
            context["mess"] = "代码无法运行"
            submit_status.user_code_status = "代码无法运行"
            submit_status.save()
            return render(request, template_name="judger_problem/templates/problem_detail.html", context=context)

        # 用户代码可运行，检测答案是否正确
        if problem.problem_output == result["output"]:
            context["status"] = "success"
            context["mess"] = "答案正确"
            submit_status.user_code_status = "正确"
        else:
            context["status"] = "success"
            context["mess"] = "答案错误，请检查你的代码逻辑"
            submit_status.user_code_status = "错误"
        submit_status.save()
        return render(request, template_name="judger_problem/templates/problem_detail.html", context=context)




