# Generated by Django 3.0.7 on 2020-06-12 07:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('judger_problem', '0013_delete_classrecode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='fk_author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='作者'),
        ),
    ]
