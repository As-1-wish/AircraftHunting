# Generated by Django 3.2.18 on 2023-05-13 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontEnd', '0002_recording_track'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recording',
            name='demoName',
        ),
    ]