# Generated by Django 2.2.24 on 2021-09-22 06:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0010_track_is_pronunciatable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listenhistory',
            name='is_pronunciatable',
        ),
        migrations.RemoveField(
            model_name='track',
            name='is_pronunciatable',
        ),
    ]
