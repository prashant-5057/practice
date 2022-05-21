from django.core.management.base import BaseCommand, CommandError
from restaurant.models import Restaurant


def find_duplicated_restaurants():
    res_list = Restaurant.objects.all()
    duplicate_restaurants = list()
    for restaurant in res_list:
        temp_res_list = Restaurant.objects.filter(
            name=restaurant.name,
            city=restaurant.city,
            address=restaurant.address)
        if temp_res_list.count() > 1:
            duplicate_restaurants += list(temp_res_list.order_by('pk')[1:])
    return duplicate_restaurants


class Command(BaseCommand):
    help = 'Show duplicate restaurants from the database.'

    def handle(self, *args, **options):
        print(find_duplicated_restaurants())
