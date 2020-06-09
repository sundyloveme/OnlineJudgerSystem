from django.db import models
from django.contrib.auth.models import User


class ProblemLabel(models.Model):
    """
    题目标签的数据模型
    """

    name = models.CharField(max_length=128, verbose_name="标签名称")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="标签创建题目时间")
    fk_author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="作者")

    class Meta:
        verbose_name = verbose_name_plural = "题目标签"

    def __str__(self):
        return self.name


class Problem(models.Model):
    """
    作业题目的数据模型
    """

    @classmethod
    def get_problem_list(cls):
        return cls.objects.all().only("title", "fk_author", "difficulty", "explains", "Submits",
                                      "corrects")

    @classmethod
    def get_liked_conut(cls, id):
        """
        获取题目为id的被点赞数量
        :return:
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
    problem_content = models.TextField(verbose_name="题目内容")
    problem_input = models.CharField(max_length=128, verbose_name="样例输入")
    problem_output = models.CharField(max_length=128, verbose_name="样例输出")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建题目时间")
    difficulty = models.IntegerField(null=True, choices=diff, verbose_name="难度")
    explains = models.IntegerField(default=0, verbose_name="题目题解数量")
    fk_labels = models.ManyToManyField(to=ProblemLabel, related_name="problem", verbose_name="题目标签")
    Submits = models.IntegerField(default=0, verbose_name="总的用户提交次数")
    corrects = models.IntegerField(default=0, verbose_name="总的用户正确次数")
    # TODO 这里不需要联机删除，但是没有on_delete参数不行
    fk_author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="作者")
    fk_liked_user = models.ManyToManyField(to=User, related_name="liked_user", verbose_name="点赞的用户")
    fk_collect_user = models.ManyToManyField(to=User, related_name="collect_user", verbose_name="收藏的用户")

    class Meta:
        verbose_name = "题目列表"
        verbose_name_plural = "题目列表"

    def __str__(self):
        return "{}".format(self.title)


class SubmitStatus(models.Model):
    """
    判题状态的数据模型
    """
    fk_problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, verbose_name="外键题目id")
    user_code_content = models.CharField(default="", max_length=128, verbose_name="用户代码")
    user_code_status = models.CharField(default="", max_length=56, verbose_name="提交状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="提交代码时间")
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="作者")

    class Meta:
        verbose_name_plural = "提交状态"
        verbose_name = "提交状态"


class Notes(models.Model):
    """
    用户笔记本
    """
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="作者")
    create_time = models.DateTimeField(auto_now=True, verbose_name="保存笔记的时间")
    fk_problem = models.ForeignKey(to=Problem, on_delete=models.CASCADE, verbose_name="题目")
    content = models.CharField(max_length=1024, verbose_name="笔记内容")

    def __str__(self):
        return "笔记内容:{}".format(self.content)


class ClassRecode(models.Model):
    """
    用户上课记录
    """
    states = [
        (0, '未上课'),
        (1, '取消'),
        (2, '已上课')
    ]

    fk_user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="user_recode", verbose_name="用户名")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建上课记录时间")
    recode_time = models.DateTimeField(verbose_name="排的上课时间")
    recode_states = models.IntegerField(choices=states, verbose_name="上课记录的状态")
    recode_video = models.CharField(max_length=128, verbose_name="上课视频地址")
    recode_enter = models.CharField(max_length=128, verbose_name="上课入口地址")
    fk_homework = models.ManyToManyField(to=Problem, related_name="homework_recode", verbose_name="作业题目")
    fk_teacher = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="上课教师")

    class Meta:
        verbose_name = "上课记录"
        verbose_name_plural = "上课记录"
