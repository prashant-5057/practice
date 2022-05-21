import json
import os

import requests
from django.db.models import F
from django.db.models.signals import (m2m_changed, post_delete, post_save,
                                      pre_delete)
from django.dispatch import receiver
from fcm_django.models import FCMDevice
from users.models import User

from restaurant.models import (MenuItem, PushNotification, Restaurant,
                               RestaurantAddExcel, SaveMenuItem)

from .tasks import restaurant_adeed_on_excel


def favourite_add_remove(sender, instance, reverse, model, **kwargs):
    _id, = kwargs['pk_set'] if kwargs['pk_set'] else (0,)

    if kwargs['action'] == 'post_add' and _id:
        model.objects.filter(id=_id).update(
            total_favourites=F('total_favourites')+1)

    if kwargs['action'] == 'pre_remove' and _id:
        if model._meta.model_name == "restaurant":
            if User.objects.filter(id=instance.id, favourite_restaurants=_id):
                model.objects.filter(id=_id).update(
                    total_favourites=F('total_favourites')-1)
        elif model._meta.model_name == "menuitem":
            if User.objects.filter(id=instance.id, favourite_menu_items=_id):
                model.objects.filter(id=_id).update(
                    total_favourites=F('total_favourites')-1)


m2m_changed.connect(favourite_add_remove,
                    sender=User.favourite_menu_items.through)

m2m_changed.connect(favourite_add_remove,
                    sender=User.favourite_restaurants.through)


@receiver(post_save, sender=SaveMenuItem)
def memu_item_total_save_add(sender, instance, created, **kwargs):
    MenuItem.objects.filter(id=instance.menu_item_id).update(
        total_saves=F('total_saves')+1)


@receiver(post_delete, sender=SaveMenuItem)
def memu_item_total_save_remove(sender, instance, **kwargs):
    MenuItem.objects.filter(id=instance.menu_item_id).update(
        total_saves=F('total_saves')-1)


@receiver(pre_delete, sender=User)
def remove_favourite_restaurant(sender, instance, **kwargs):
    remove_restro_like = instance.favourite_restaurants.all().values_list('id', flat=True)
    if remove_restro_like:
        Restaurant.objects.filter(id__in=remove_restro_like).update(
            total_favourites=F('total_favourites')-1)


@receiver(pre_delete, sender=User)
def remove_favourite_menuitem(sender, instance, **kwargs):
    remove_menu_like = instance.favourite_menu_items.all().values_list('id', flat=True)
    if remove_menu_like:
        MenuItem.objects.filter(id__in=remove_menu_like).update(
            total_favourites=F('total_favourites')-1)


@receiver(post_save, sender=RestaurantAddExcel)
def restaurant_added_on_excel(sender, instance, created, **kwargs):
    if instance.restaurant_excel:
        restaurant_adeed_on_excel(pk=instance.pk)
        # restaurant_adeed_on_excel.delay(pk=instance.pk)


def prepate_notification_data(instance, notification_data_image=''):
    return {
        "id": instance.id,
        "name": instance.name,
        "address": instance.address,
        "city": instance.city,
        "state": instance.state,
        "zip_code": instance.zip_code,
        "email": instance.email,
        "phone_number": instance.phone_number,
        "owner_or_manager": instance.owner_or_manager,
        "picture": instance.picture.url if instance.picture else "",
        "website": instance.website,
        "industry": instance.industry,
        "description": instance.description,
        "total_favourites": instance.total_favourites,
        "restaurant_owner_id": instance.restaurant_owner_id,
        "menus": json.dumps(list(MenuItem.objects.filter(restaurant=instance.id).values('pk', 'menu', 'name', 'total_favourites', 'total_saves', 'menu_image'))),
    }


def push_notification_send(deviceTokens, notification, dataPayLoad):
    serverToken = os.getenv("FCM_SERVER_KEY")
    if serverToken:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]

        deviceTokensList = list(divide_chunks(deviceTokens, 900))
        for fcm_token_list in deviceTokensList:
            body = {
                'content_available': True,
                'mutable_content': True,
                'notification': notification,
                'registration_ids': fcm_token_list,
                'priority': 'high',
                'data': dataPayLoad,
            }
            response = requests.post(
                "https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))


@receiver(post_save, sender=PushNotification)
def send_custom_notification(sender, instance, **kwargs):
    all_devices = FCMDevice.objects.order_by(
        'device_id', '-id').distinct('device_id')

    notification_data = dict()
    notification_data["title"] = instance.title
    notification_data["body"] = instance.message if instance.message else ''
    notification_data["image"] = instance.image.url if instance.image else ''

    restaurant_data = {}
    if instance.restaurant:
        restaurant_data = prepate_notification_data(
            instance.restaurant, notification_data["image"])

    PushNotification.objects.update(
        title="", message="", image="", restaurant="")

    device_token_list = all_devices.exclude(registration_id__isnull=True).exclude(
        registration_id='null').values_list('registration_id', flat=True)

    # push notification send all device.
    push_notification_send(
        device_token_list, notification_data, restaurant_data)
