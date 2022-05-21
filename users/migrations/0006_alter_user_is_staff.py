# Generated by Django 3.2.4 on 2021-11-26 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether this user can log into this admin site.', verbose_name='Restaurant owner'),
        ),
    ]
