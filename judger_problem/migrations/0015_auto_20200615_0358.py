# Generated by Django 3.0.7 on 2020-06-15 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judger_problem', '0014_auto_20200612_0712'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='problem_std_code',
            field=models.TextField(default='', verbose_name='标准代码'),
        ),
        migrations.AddField(
            model_name='problem',
            name='problem_test_case_input',
            field=models.TextField(default='', verbose_name='输入测试用例'),
        ),
        migrations.AddField(
            model_name='problem',
            name='problem_test_case_output',
            field=models.TextField(default='', verbose_name='输出测试用例'),
        ),
    ]