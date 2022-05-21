import json

from rest_framework import serializers

from .models import (BannerImage, MenuItem, ReportSearchText, Restaurant,
                     SaveMenuItem,RestaurantAddresses)


class BannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = ('image',)


class MenuItemSerlizers(serializers.ModelSerializer):
    menu_image = serializers.SerializerMethodField()
    restaurant = serializers.SerializerMethodField('get_restaurant')
    menu_category = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ('restaurant', 'menu_category', 'id',  'name', 'total_favourites',
                  'total_saves', 'menu_image',)

    def get_menu_image(self, obj):
        return obj.menu_image.url if obj.menu_image else ''

    def get_menu_category(self, obj):
        return {
            'id': obj.menu.id,
            'order': obj.menu.order,
            'name': obj.menu.name,
        } if obj.menu else None

    def get_restaurant(self, obj):
        restaurant_details = {'id': obj.restaurant.id,
                              'name': obj.restaurant.name,
                              'address': obj.restaurant.address,
                              'city': obj.restaurant.city,
                              'state': obj.restaurant.state,
                              'zip_code': obj.restaurant.zip_code,
                              'phone_number': obj.restaurant.phone_number,
                              }
        return restaurant_details

class RestaurantLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantAddresses
        fields = '__all__'


class RestaurantAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantAddresses
        fields = ('id','latitude','longitude', 'address', 'city', 'state', 'zipcode')

class RestaurantSerializer(serializers.ModelSerializer):
    banner_images = serializers.StringRelatedField(
        source='bannerimage_set', many=True)
    menus = serializers.SerializerMethodField('get_menu_items')
    restaurant_addresses = serializers.SerializerMethodField('get_restaurant_addresses')

    def get_menu_items(self, instance):
        menuItems = []
        menu_items_all = instance.menuitem_set.all()
        menuIdList = menu_items_all.values_list(
            'menu_id', flat=True).distinct()
        for menuId in menuIdList:
            menuItemsObjs = MenuItem.objects.filter(
                menu=menuId, restaurant=instance.id).order_by('-total_favourites')
            for menuItemObj in menuItemsObjs:
                menuItems.append(MenuItemSerlizers(menuItemObj).data)
        return menuItems

        # menuItems = []
        # for item in menu_items_all:
        #     menuItems.append(MenuItemSerlizers(item).data)
        # return menuItems

    def get_restaurant_addresses(self, instance):
        restaurant_addresses = RestaurantAddresses.objects.filter(restaurant_id=instance.id)
        response = RestaurantAddressSerializer(restaurant_addresses, many=True).data
        return response

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'address', 'city', 'state', 'zip_code', 'email',
                  'phone_number', 'owner_or_manager', 'picture', 'website', 'industry','restaurant_addresses', 'banner_images', 'menus', 'total_favourites',)


class SaveMenuItemSerlizers(serializers.ModelSerializer):
    menu_item = MenuItemSerlizers()

    class Meta:
        model = SaveMenuItem
        fields = ('user_id', 'created_at', 'menu_item')


class ReportSearchTextSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportSearchText
        fields = ('search_text',)
