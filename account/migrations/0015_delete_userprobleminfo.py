# Generated by Django 3.0.7 on 2020-08-09 06:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_userprobleminfo'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProblemInfo',
        ),
    ]