# Generated by Django 2.2.12 on 2021-06-08 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20210608_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_uploadable',
            field=models.BooleanField(default=False),
        ),
    ]
