# Generated by Django 2.2 on 2020-05-27 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judger_problem', '0006_auto_20200527_0646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submitstatus',
            name='user_code_status',
            field=models.CharField(default='', max_length=56, verbose_name='提交状态'),
        ),
    ]
