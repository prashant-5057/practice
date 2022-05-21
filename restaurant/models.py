

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.utils.translation import ugettext as _
from solo.models import SingletonModel

phone_number_validation = RegexValidator(
    r'^(\+\d{1,3}[- ]?)?\d{10}$', 'Please enter valid phone number.')

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, blank=True, null=True)
    # phone_number = PhoneNumberField(blank=True, null=True, help_text='(e.g +918457221548, +33123456789)')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    owner_or_manager = models.CharField(max_length=255, blank=True, null=True)
    picture = models.ImageField(
        upload_to='restaurant-picture', blank=True, null=True)
    website = models.CharField(max_length=2000, blank=True, null=True)
    industry = models.CharField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    total_favourites = models.PositiveIntegerField(default=0)
    restaurant_owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"
        db_table = 'restaurant'
        ordering = ['total_favourites']


class RestaurantAddExcel(SingletonModel):
    restaurant_excel = models.FileField(
        upload_to='restaurant-excel', validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'xlsm', 'csv'])])

    def __str__(self):
        return 'Restaurant Excel'

    class Meta:
        verbose_name = "Restaurant Add Excel"
        verbose_name_plural = "Restaurant Add Excels"
        db_table = 'restaurant_excel'


class BannerImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banner-image',)

    def __str__(self):
        return self.image.url

    class Meta:
        verbose_name = "Banner Image"
        verbose_name_plural = "Banner Images"
        db_table = 'banner_image'


class Menu(models.Model):
    name = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        db_table = 'menus'
        ordering = ['order']

    def clean(self):
        if Menu.objects.filter(name__iexact=self.name).first():
            raise ValidationError("Menu with this Name already exists.")


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu = models.ForeignKey(
        Menu, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=500)
    total_favourites = models.PositiveIntegerField(default=0)
    total_saves = models.PositiveIntegerField(default=0)
    menu_image = models.ImageField(
        upload_to='menu-image', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('menu',)
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        db_table = 'menu_item'


class SaveMenuItem(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.menu_item.name

    class Meta:
        verbose_name = "Save Menu Item"
        verbose_name_plural = "Save Menu Items"
        db_table = 'save_menu_item'


class ReportSearchText(models.Model):
    search_text = models.CharField(max_length=100)

    def __str__(self):
        return self.search_text

    class Meta:
        verbose_name = "Report Search Text"
        verbose_name_plural = "Report Search Texts"
        db_table = 'report_search_text'

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

class RestaurantAddresses(models.Model):
    """Manage multiple restaurant addresses.
    """
    location = models.PointField(help_text="Use map widget for point the restaurant location", null=True, blank=True)
    latitude = models.FloatField(_("Latitude"), null=True, blank=True,
                                 help_text="Latitude is an angle (defined below) which ranges from 0° at the Equator to 90° (North or South) at the poles.")
    longitude = models.FloatField(_("Longitude"), null=True, blank=True,
                                   help_text="Longitude is the measurement east or west of the prime meridian")
    address = models.TextField(_("Address"), null=True, blank=True)
    city = models.CharField(_("City"), max_length=255, null=True, blank=True)
    state = models.CharField(_("State"), max_length=255, null=True, blank=True)
    zipcode = models.CharField(
        _("Zip code"), max_length=255, null=True, blank=True)
    restaurant = models.ForeignKey(
        Restaurant, related_name="restaurant_addresses", on_delete=models.CASCADE, verbose_name="Restaurant")

class PushNotification(SingletonModel):
    title = models.CharField(
        max_length=255, help_text="Add notification title here.")
    message = models.TextField(
        help_text="Add notification message here.")
    image = models.ImageField(
        upload_to='notification_image', null=True, blank=True)
    restaurant = models.ForeignKey(
        Restaurant, related_name="restaurant_name",  on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Push Notification {self.title}"

    class Meta:
        verbose_name = "Send Push Notification"
