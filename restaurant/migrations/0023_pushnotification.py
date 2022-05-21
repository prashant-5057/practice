# Generated by Django 3.2.4 on 2021-11-26 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0022_restaurant_restaurant_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Add notification title here.', max_length=255)),
                ('message', models.TextField(blank=True, help_text='Add notification message here.', null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='notification_image')),
                ('restaurant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_name', to='restaurant.restaurant')),
            ],
            options={
                'verbose_name': 'Send Push Notification',
            },
        ),
    ]
