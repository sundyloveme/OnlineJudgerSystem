# Generated by Django 2.2 on 2020-06-09 07:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20200609_0753'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userinfo',
            options={'verbose_name': '用户信息', 'verbose_name_plural': '用户信息'},
        ),
        migrations.AddField(
            model_name='classrecode',
            name='comment',
            field=models.TextField(default='', verbose_name='讲师点评'),
        ),
        migrations.AlterField(
            model_name='classrecode',
            name='fk_teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='上课讲师'),
        ),
    ]
