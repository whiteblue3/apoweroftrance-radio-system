# Generated by Django 2.2 on 2020-04-20 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0005_remove_playqueue_will_play_at'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PlayQueue',
        ),
    ]
