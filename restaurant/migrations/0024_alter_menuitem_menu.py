# Generated by Django 3.2.4 on 2021-12-07 13:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0023_pushnotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restaurant.menu'),
        ),
    ]
