# Generated by Django 3.0.7 on 2020-08-09 06:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0013_auto_20200809_0455'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProblemInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.CharField(max_length=128)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_right', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
