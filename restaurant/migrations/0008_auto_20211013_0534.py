# Generated by Django 3.2.4 on 2021-10-13 05:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0007_auto_20211008_0435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z& ]*$', 'Only alphanumeric characters are allowed.')]),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='city',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z& ]*$', 'Only alphanumeric characters are allowed.')]),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='name',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z& ]*$', 'Only alphanumeric characters are allowed.')]),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='state',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z& ]*$', 'Only alphanumeric characters are allowed.')]),
        ),
        migrations.AlterUniqueTogether(
            name='menuitem',
            unique_together={('restaurant', 'name')},
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='menu',
        ),
    ]
