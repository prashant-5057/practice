# Generated by Django 3.2.4 on 2022-03-03 12:10

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0031_auto_20220225_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestaurantAddresses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, help_text='Use map widget for point the restaurant location', null=True, srid=4326)),
                ('latitude', models.FloatField(blank=True, help_text='Latitude is an angle (defined below) which ranges from 0° at the Equator to 90° (North or South) at the poles.', null=True, verbose_name='Latitude')),
                ('longitude', models.FloatField(blank=True, help_text='Longitude is the measurement east or west of the prime meridian', null=True, verbose_name='Longitude')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Address')),
                ('city', models.CharField(blank=True, max_length=255, null=True, verbose_name='City')),
                ('state', models.CharField(blank=True, max_length=255, null=True, verbose_name='State')),
                ('zipcode', models.CharField(blank=True, max_length=255, null=True, verbose_name='Zip code')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_addresses', to='restaurant.restaurant', verbose_name='Restaurant')),
            ],
        ),
    ]
