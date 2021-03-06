# Generated by Django 3.2.4 on 2022-02-25 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0029_auto_20220207_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='latitude',
            field=models.FloatField(blank=True, help_text='Latitude is an angle (defined below) which ranges from 0° at the Equator to 90° (North or South) at the poles.', null=True, verbose_name='Latitude'),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='longitude',
            field=models.FloatField(blank=True, help_text='Longitude is the measurement east or west of the prime meridian', null=True, verbose_name='Longitude'),
        ),
    ]
