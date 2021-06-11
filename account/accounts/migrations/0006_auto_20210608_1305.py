# Generated by Django 2.2.12 on 2021-06-08 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_is_uploadable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='is_business',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_uploadable',
        ),
        migrations.AddField(
            model_name='user',
            name='is_business',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_uploadable',
            field=models.BooleanField(default=True),
        ),
    ]
