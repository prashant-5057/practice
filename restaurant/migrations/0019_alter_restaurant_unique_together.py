# Generated by Django 3.2.4 on 2021-11-01 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0018_alter_menuitem_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='restaurant',
            unique_together=set(),
        ),
    ]
