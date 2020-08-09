from django.db import models
from django.contrib.auth.models import User
from judger_problem.models import Problem

from mdeditor.fields import MDTextField


class UserInfo(models.Model):
    """
    用户的个人信息数据模型
    """

    iphone = models.CharField(max_length=64, verbose_name="手机号")
    info = models.TextField(verbose_name="用户个人简介")
    motto = models.CharField(max_length=128, verbose_name="用户个性签名")
    photo = models.ImageField(verbose_name="用户照片")
    user = models.OneToOneField(to=User, related_name="user_info",
                                on_delete=models.CASCADE,
                                verbose_name="User表外键")
    right_problems = models.ManyToManyField(to=Problem, verbose_name="正确题目列表")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"


class ClassRecode(models.Model):
    """
    用户的上课记录
    """
    states = [
        (0, '未上课'),
        (1, '取消'),
        (2, '已上课')
    ]

    fk_user = models.ForeignKey(to=User,
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name="user_recode",
                                verbose_name="用户名")

    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name="创建上课记录时间")

    recode_time = models.DateTimeField(verbose_name="排的上课时间")

    recode_states = models.IntegerField(choices=states,
                                        default=0,
                                        verbose_name="上课记录的状态")

    recode_video = models.CharField(blank=True,
                                    max_length=128,
                                    verbose_name="上课视频地址")

    recode_enter = models.CharField(blank=True,
                                    max_length=128,
                                    verbose_name="上课入口地址")

    fk_homework = models.ManyToManyField(blank=True,
                                         to=Problem,
                                         related_name="homework_recode",
                                         verbose_name="作业题目")

    fk_teacher = models.ForeignKey(to=User,
                                   null=True,
                                   on_delete=models.SET_NULL,
                                   verbose_name="上课讲师")

    comment = MDTextField(default="",
                          blank=True,
                          verbose_name="讲师点评")

    tiquma = models.CharField(max_length=128,
                              default="",
                              blank=True,
                              verbose_name="视频提取码")

    class Meta:
        verbose_name = "上课记录"
        verbose_name_plural = "上课记录"

    def __str__(self):
        return "<{},{}>".format(self.fk_user, self.recode_time)
