# Generated by Django 3.2.4 on 2021-10-06 05:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('restaurant', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('full_name', models.CharField(blank=True, max_length=255)),
                ('email', models.EmailField(max_length=255, null=True, unique=True)),
                ('provider_type', models.CharField(choices=[('google', 'Google'), ('facebook', 'Facebook'), ('apple', 'Apple'), ('sapid_app', 'Sapid App')], default='sapid_app', max_length=20)),
                ('provider_user_id', models.CharField(blank=True, max_length=255)),
                ('device_id', models.CharField(max_length=255)),
                ('device_type', models.CharField(choices=[('android', 'Android'), ('ios', 'IOS')], max_length=10)),
                ('favourite_menu_items', models.ManyToManyField(blank=True, related_name='favourite_menu_items', to='restaurant.MenuItem', verbose_name='Favourite Menu Items')),
                ('favourite_restaurants', models.ManyToManyField(blank=True, related_name='favourite_restaurants', to='restaurant.Restaurant', verbose_name='Favourite Restaurants')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('save_menu_items', models.ManyToManyField(blank=True, related_name='save_menu_items', to='restaurant.MenuItem', verbose_name='Save Menu Items')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'users',
                'ordering': ['id', 'email'],
            },
        ),
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Add notification title here.', max_length=255)),
                ('message', models.TextField(blank=True, help_text='Add notification message here.', null=True)),
                ('image', models.ImageField(blank=True, help_text='Image view on recived notification.', null=True, upload_to='notification-image')),
                ('restaurant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restaurant.restaurant')),
            ],
            options={
                'verbose_name': 'Send Push Notification',
                'verbose_name_plural': 'Send Push Notifications',
                'db_table': 'push_notification',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('feedback_type', models.CharField(choices=[('overall_service', 'Overall Service'), ('customer_support', 'Customer Support'), ('add_restaurant', 'Add Restaurant')], max_length=20)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Feedback',
                'verbose_name_plural': 'Feedbacks',
                'db_table': 'feedback',
            },
        ),
    ]