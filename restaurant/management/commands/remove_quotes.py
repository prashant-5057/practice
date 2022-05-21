import ast

from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from django.utils import timezone
from restaurant.models import MenuItem


class Command(BaseCommand):
    help = "Remove qoutes from menu-item names"

    def handle(self, *args, **kwargs):
        menuitem = MenuItem.objects.all()
        for menu in menuitem:
            if menu.name == '\"\"':
                menu.delete()
            else:
                menu.name = menu.name.strip('"')
                menu.save()
        self.stdout.write("Removed double quotes from menu-item names.")
