from django.db import models
from django.contrib.auth.models import User

from mdeditor.fields import MDTextField


class ProblemLabel(models.Model):
    """
    题目标签的数据模型
    """

    name = models.CharField(max_length=128, verbose_name="标签名称")
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name="标签创建题目时间")
    fk_author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                                  verbose_name="作者")

    class Meta:
        verbose_name = verbose_name_plural = "题目标签"

    def __str__(self):
        return self.name


class Problem(models.Model):
    """
    题目的数据模型
    """

    @classmethod
    def get_sth_problem_list(cls, key_word):
        """
        搜索题目
        :param key_word: 关键字
        :return: 搜索结果
        """
        return cls.objects.filter(title__contains=key_word)

    @classmethod
    def get_problem_list(cls):
        """
        相当于 select 部分字段 from Problem
        :return: 查询结果
        """
        return cls.objects.all().only("title", "fk_author", "difficulty",
                                      "explains", "Submits",
                                      "corrects")

    @classmethod
    def get_liked_conut(cls, id):
        """
        获取id为id的题目的点赞数量
        :return: 点赞数量
        """
        return cls.objects.get(id=id).fk_liked_user.count()

    @classmethod
    def get_collect_count(cls, id):
        """
        获取题目为id的被收藏数量
        :param id: 题目id
        :return: 被收藏总数
        """
        return cls.objects.get(id=id).fk_collect_user.count()

    diff = [
        (0, "简单"),
        (1, "中等"),
        (2, "困难"),
    ]
    title = models.CharField(max_length=128, verbose_name="题目标题")
    # problem_content = models.TextField(verbose_name="题目内容")
    problem_content = MDTextField(verbose_name="题目内容")
    problem_input = models.TextField(blank=True, verbose_name="样例输入")
    problem_output = models.TextField(blank=True, verbose_name="样例输出")
    problem_test_case_input = models.TextField(default="",
                                               verbose_name="输入测试用例",
                                               help_text="以'///'分割多个数据")
    problem_test_case_output = models.TextField(default="",
                                                verbose_name="输出测试用例",
                                                help_text="以'///'分割多个数据")
    problem_input_style = models.TextField(default="", blank=True,
                                           verbose_name="输入格式")
    problem_output_style = models.TextField(default="", blank=True,
                                            verbose_name="输出格式")
    problem_std_code = models.TextField(blank=True, default="",
                                        verbose_name="标准代码")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建题目时间")
    difficulty = models.IntegerField(null=True, blank=True, choices=diff,
                                     verbose_name="难度")
    explains = models.IntegerField(default=0, blank=True, verbose_name="题目题解数量")
    fk_labels = models.ManyToManyField(to=ProblemLabel, blank=True,
                                       related_name="problem",
                                       verbose_name="题目标签")
    Submits = models.IntegerField(default=0, blank=True,
                                  verbose_name="总的用户提交次数")
    corrects = models.IntegerField(default=0, blank=True,
                                   verbose_name="总的用户正确次数")
    fk_author = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL,
                                  verbose_name="作者")
    fk_liked_user = models.ManyToManyField(
        to=User, blank=True, related_name="liked_user", verbose_name="点赞的用户")
    fk_collect_user = models.ManyToManyField(
        to=User, blank=True, related_name="collect_user", verbose_name="收藏的用户")

    class Meta:
        verbose_name = "题目列表"
        verbose_name_plural = "题目列表"

    def __str__(self):
        return "{}".format(self.title)


class SubmitStatus(models.Model):
    """
    判题状态的数据模型
    """
    fk_problem_id = models.ForeignKey(Problem,
                                      on_delete=models.CASCADE,
                                      verbose_name="外键题目id")

    user_code_content = models.CharField(default="",
                                         max_length=1024,
                                         verbose_name="用户代码")

    user_code_status = models.CharField(default="",
                                        max_length=56,
                                        verbose_name="提交状态")

    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name="提交代码时间")

    author = models.ForeignKey(to=User,
                               on_delete=models.CASCADE,
                               related_name="submit_status",
                               verbose_name="作者")

    class Meta:
        verbose_name_plural = "提交状态"
        verbose_name = "提交状态"

    def __str__(self):
        return "<{},{}>".format(self.fk_problem_id.title, self.user_code_status)


class Notes(models.Model):
    """
    用户笔记本
    """
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               verbose_name="作者")
    create_time = models.DateTimeField(auto_now=True, verbose_name="保存笔记的时间")
    fk_problem = models.ForeignKey(to=Problem, on_delete=models.CASCADE,
                                   verbose_name="题目")
    content = models.CharField(max_length=1024, verbose_name="笔记内容")

    def __str__(self):
        return "笔记内容:{}".format(self.content)
