# Generated by Django 2.2.12 on 2021-06-01 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0005_auto_20210601_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='like',
            field=models.BooleanField(default=False),
        ),
    ]
