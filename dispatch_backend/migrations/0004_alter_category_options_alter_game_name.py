# Generated by Django 4.0.3 on 2022-04-15 14:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch_backend', '0003_game_server_id_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AlterField(
            model_name='game',
            name='name',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z-_]*$', 'Only alphanumeric characters or underscore or dash are allowed.')]),
        ),
    ]
