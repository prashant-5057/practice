from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from push_notifications.models import APNSDevice, GCMDevice
from solo.admin import SingletonModelAdmin
from django.contrib.gis import admin as GisAdmin
from django.contrib.gis.db import models
from mapwidgets.widgets import GooglePointFieldInlineWidget

from .models import (BannerImage, Menu, MenuItem, PushNotification,
                     ReportSearchText, Restaurant, RestaurantAddExcel, RestaurantAddresses)

admin.site.register(RestaurantAddExcel, SingletonModelAdmin)
admin.site.register(ReportSearchText)
admin.site.register(PushNotification, SingletonModelAdmin)
admin.site.unregister(APNSDevice)
admin.site.unregister(GCMDevice)

@admin.register(RestaurantAddresses)
class RestaurantAddressesListAdmin(admin.ModelAdmin):
    list_display = ('restaurant',  'address', 'city', 'state', 'zipcode', 'latitude', 'longitude')
    exclude = ('location',)

class BannerImageInline(admin.TabularInline):
    model = BannerImage
    extra = 0
    max_num = 5

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class MenuItemInline(admin.TabularInline):
    model = MenuItem

    extra = 0
    max_num = 200
    readonly_fields = ('total_favourites', 'total_saves')
    list_display = ['name']
    list_display_links = ['name']

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Menu)
class MenuAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['order', 'name']

class RestaurantAddressesAdmin(GisAdmin.StackedInline):
    model = RestaurantAddresses
    extra = 0
    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldInlineWidget}
    }
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'picture_get', 'address', 'city', 'state',
                    'zip_code', 'email', 'phone_number', 'restaurant_owner', 'website', 'industry', 'favourites', 'item_saves', 'item_favourites')
    readonly_fields = ('total_favourites',)
    search_fields = ('name', 'address', 'city', 'state', 'zip_code')

    def favourites(self, obj):
        return obj.total_favourites

    def item_saves(self, obj):
        menu_items = MenuItem.objects.filter(
            restaurant_id=obj.id).aggregate(Sum('total_saves'))
        return menu_items['total_saves__sum']

    def item_favourites(self, obj):
        menu_items = MenuItem.objects.filter(
            restaurant_id=obj.id).aggregate(Sum('total_favourites'))
        return menu_items['total_favourites__sum']

    def has_module_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        if request.user.is_staff and not request.user.is_superuser:
            return obj is None or Restaurant.objects.filter(restaurant_owner=request.user.pk)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_staff and not request.user.is_superuser:
            return obj is None or Restaurant.objects.filter(restaurant_owner=request.user.pk)
        else:
            return True

    def get_queryset(self, request):
        if request.user.is_staff and not request.user.is_superuser:
            restaurant = Restaurant.objects.filter(
                restaurant_owner=request.user.pk)
            return restaurant
        else:
            restaurants = Restaurant.objects.all()
            return restaurants

    def picture_get(self, obj):
        return format_html('<img src="{}" width="auto" height="50px" />'.format(obj.picture.url)) if obj.picture else '-'
    picture_get.short_description = "Picture"

    def get_form(self, request, obj=None, **kwargs):
        """Remove restaurant owner field if a user is a restaurant owner. 
        """
        if request.user.is_superuser:
            self.exclude = ()
        else:
            self.exclude = ('restaurant_owner',)
        return super(RestaurantAdmin, self).get_form(request, obj=None, **kwargs)

    def save_model(self, request, obj, form, change):
        """Save current login user id for the restaurant owner.
        """
        if request.user.is_staff and not request.user.is_superuser:
            if not obj.restaurant_owner_id:
                obj.restaurant_owner_id = request.user.id

        super(RestaurantAdmin, self).save_model(request, obj, form, change)

    inlines = [
        BannerImageInline,
        MenuItemInline,
        RestaurantAddressesAdmin
    ]
