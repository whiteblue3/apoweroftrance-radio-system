# Generated by Django 2.2.24 on 2021-06-29 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20210628_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
