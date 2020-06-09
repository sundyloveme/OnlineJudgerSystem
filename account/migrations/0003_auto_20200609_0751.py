# Generated by Django 2.2 on 2020-06-09 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_classrecode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classrecode',
            name='fk_homework',
            field=models.ManyToManyField(blank=True, related_name='homework_recode', to='judger_problem.Problem', verbose_name='作业题目'),
        ),
        migrations.AlterField(
            model_name='classrecode',
            name='recode_enter',
            field=models.CharField(blank=True, max_length=128, verbose_name='上课入口地址'),
        ),
        migrations.AlterField(
            model_name='classrecode',
            name='recode_video',
            field=models.CharField(blank=True, max_length=128, verbose_name='上课视频地址'),
        ),
    ]