# Generated by Django 2.2 on 2020-04-14 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0002_auto_20200415_0611'),
    ]

    operations = [
        migrations.RenameField(
            model_name='like',
            old_name='created_at',
            new_name='updated_at',
        ),
    ]