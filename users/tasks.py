from celery import shared_task

from .models import PushNotification


@shared_task
def push_notification_send_all_user(pk):
    PushNotification.objects.get(pk=pk)
    return "Notification Send to all user."
