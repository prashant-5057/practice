# Generated by Django 3.2.4 on 2021-11-01 06:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0017_alter_reportsearchtext_search_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(max_length=500, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z& ]*$', 'Only alphanumeric characters are allowed.')]),
        ),
    ]