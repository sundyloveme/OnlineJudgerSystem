# Generated by Django 2.2 on 2020-06-05 08:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('judger_problem', '0009_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='fk_liked_user',
            field=models.ManyToManyField(related_name='liked_user', to=settings.AUTH_USER_MODEL, verbose_name='点赞的用户'),
        ),
    ]
