# Generated by Django 4.0.3 on 2024-05-01 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch_backend', '0015_populate_channels_in_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='channel',
        ),
    ]