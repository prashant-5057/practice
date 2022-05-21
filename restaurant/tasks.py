import os
from venv import create

import pandas as pd
# from celery import shared_task
from django.db import transaction

from .models import MenuItem, Restaurant, RestaurantAddExcel, RestaurantAddresses


# @shared_task
def restaurant_adeed_on_excel(pk):
    uploded_file = RestaurantAddExcel.objects.get(pk=pk)
    name, extension = os.path.splitext(uploded_file.restaurant_excel.name)

    xl = pd.ExcelFile(uploded_file.restaurant_excel)
    sheetnames = xl.sheet_names  # see all sheet names

    for idx, _ in enumerate(sheetnames):
        restaurants = pd.read_excel(
            uploded_file.restaurant_excel, sheet_name=idx).fillna('')

        for _, restaurant in restaurants.iterrows():
            name = restaurant['Name']
            address = restaurant['Address']
            city = restaurant['City']
            state = restaurant['State']
            try:
                zip_code = restaurant['Zip']
            except:
                zip_code = restaurant['Zip Code']

            email = restaurant['Email'] if "Email" in restaurant else ""
            phone_number = restaurant['Phone Number'] if "Phone Number" in restaurant else ""
            owner_or_manager = restaurant['Owner / Manager'] if "Owner / Manager" in restaurant else ""
            website = restaurant['Website']
            industry = restaurant['Industry']
            latitude = restaurant['Latitude'] if "Latitude" in restaurant else 0
            longitude = restaurant['Longitude'] if "Longitude" in restaurant else 0
            excl_menu_list = restaurant['Menu Items (comma separated)']
            description = restaurant['Description'] if "Description" in restaurant else ""
            restaurant_dict = {"address":address,"state": state, "email": email, "phone_number": phone_number,
                               "owner_or_manager": owner_or_manager, "website": website, "industry": industry, "description": description}
            restaurant_address_dict = {"address":address, "latitude":latitude,"longitude":longitude, "state":state}
            # try:
            #     with transaction.atomic():
            #         restaurant, created = Restaurant.objects.update_or_create(
            #             name=name, address=address, city=city, zip_code=zip_code, defaults=restaurant_dict)
            #         # menu_list = excl_menu_list.split(',')
            #         for menu in json.loads(excl_menu_list):
            #             umenuObj, cmenuObj = Menu.objects.update_or_create(name=menu)
            #             if umenuObj:
            #                 save_menu_item(restaurant, json.loads(excl_menu_list)[menu], umenuObj)
            #             else:
            #                 save_menu_item(restaurant, json.loads(excl_menu_list)[menu], cmenuObj)
            # except Exception as e:
            #     pass

            try:
                with transaction.atomic():
                    restaurant, created = Restaurant.objects.update_or_create(
                        name=name, city=city, defaults=restaurant_dict)
                    """add restaurant addresses"""
                    RestaurantAddresses.objects.update_or_create(restaurant=restaurant,city=city,zipcode=zip_code,defaults=restaurant_address_dict)


                    menu_list = excl_menu_list.split(',')
                    menu_list = [item.replace('"', '').strip()
                                 for item in menu_list if item]

                    if not created:
                        all_menues_items = MenuItem.objects.filter(
                            restaurant=restaurant).values_list('name', flat=True)
                        all_menues_items = list(all_menues_items)

                        for menu in menu_list:
                            if not menu in all_menues_items:
                                all_menues_items.append(menu)

                        set_difference = list(
                            set(all_menues_items) - set(menu_list))

                        for dif_element in set_difference:
                            all_menues_items.remove(dif_element)

                        MenuItem.objects.filter(
                            restaurant=restaurant, name__in=set_difference).delete()

                        menu_list = all_menues_items

                    for menu in menu_list:
                        save_menu_item(restaurant, menu)

            except:
                pass

    RestaurantAddExcel.objects.filter(pk=pk).update(restaurant_excel='')
    return "All restaurant added in our database on uploded excel."

# def save_menu_item(restaurant, menu_list, menuObj):
#     new_menu_item_list = []
#     for item_name in menu_list:
#         item_name = item_name.replace('"', '').strip()
#         if item_name:
#             if not MenuItem.objects.filter(restaurant=restaurant, menu=menuObj, name=item_name).exists():
#                 create = MenuItem.objects.create(
#                     restaurant=restaurant, menu=menuObj, name=item_name)


def save_menu_item(restaurant, menu):
    # for item_name in menu:
    # if item_name:
    if not MenuItem.objects.filter(restaurant=restaurant, name=menu).exists():
        create = MenuItem.objects.create(
            restaurant=restaurant, name=menu)
