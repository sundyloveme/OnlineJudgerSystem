# Generated by Django 3.0.7 on 2020-06-15 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judger_problem', '0018_auto_20200615_0417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submitstatus',
            name='user_code_content',
            field=models.CharField(default='', max_length=1024, verbose_name='用户代码'),
        ),
    ]
