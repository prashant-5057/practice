# Generated by Django 3.2.4 on 2021-12-09 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0024_alter_menuitem_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pushnotification',
            name='message',
            field=models.TextField(default='', help_text='Add notification message here.'),
            preserve_default=False,
        ),
    ]