# Generated by Django 3.2.4 on 2021-11-29 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_identifier_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]