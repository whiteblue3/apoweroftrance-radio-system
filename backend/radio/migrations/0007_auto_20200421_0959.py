# Generated by Django 2.2 on 2020-04-21 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0006_delete_playqueue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='location',
            field=models.CharField(max_length=254),
        ),
    ]
