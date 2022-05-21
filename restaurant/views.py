
from django.db.models import Sum
from django.http import Http404, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from restaurant.filter import PriorizedSearchFilter
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt, Radians
from django.db.models import F
from .models import MenuItem, Restaurant, SaveMenuItem, RestaurantAddresses
from .serializers import (MenuItemSerlizers, ReportSearchTextSerializer,
                          RestaurantSerializer, SaveMenuItemSerlizers, RestaurantLocationSerializer)
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from django.db.models import Case, When

class RestaurantApi(generics.ListAPIView):
    queryset = Restaurant.objects.all().order_by('id')
    serializer_class = RestaurantSerializer
    filter_backends = [PriorizedSearchFilter, ]
    search_fields = ['name', 'address', 'city', 'zip_code',
                     'menuitem__name', 'menuitem__menu__name']

    def list(self, request, *args, **kwargs):
        """ Return nearest restaurants if latitude and longitude provided"""
        if "search" in request.GET and request.GET["search"]:
            restaurants = Restaurant.objects.order_by(
                Case(When(name=request.GET["search"], then=0), default=1),
                'name',
            )
            print('-------'*20)
            print(restaurants)
            print('-------'*20)
            return Response(RestaurantSerializer(restaurants, many=True).data)
        if "latitude" in request.GET and "longitude" in request.GET:
            if float(request.GET["latitude"]) > 0 and float(request.GET["longitude"]) > 0:
                latitude = float(request.GET["latitude"])
                longitude = float(request.GET["longitude"])
                dlat = Radians(F('latitude') - latitude)
                dlong = Radians(F('longitude') - longitude)

                a = (Power(Sin(dlat/2), 2) + Cos(Radians(latitude)) 
                    * Cos(Radians(F('latitude'))) * Power(Sin(dlong/2), 2)
                )
                c = 2 * ATan2(Sqrt(a), Sqrt(1-a))
                d = 6371 * c
                if "search" in request.GET and request.GET["search"]:
                    restaurants_addresses = RestaurantAddresses.objects.filter(restaurant__name__icontains=request.GET["search"]).annotate(distance=d).order_by('distance')
                    if not restaurants_addresses:
                        restaurants_addresses = RestaurantAddresses.objects.filter(restaurant__name__icontains=request.GET["search"])
                else:
                    restaurants_addresses = RestaurantAddresses.objects.annotate(distance=d).order_by('distance')

                serializer = RestaurantLocationSerializer(restaurants_addresses, many=True)
                restaurants = []
                for data in serializer.data:
                    for restaurant in Restaurant.objects.filter(pk=data['restaurant']):
                        if not any(res_id['id'] == data['restaurant'] for res_id in restaurants):
                            restaurants.append(RestaurantSerializer(restaurant).data)
                            for res in restaurants:
                                if res['id'] == data['restaurant']:
                                    res['restaurant_addresses'] = []
                                    res['restaurant_addresses'].append({'id':data['id'],'latitude':data['latitude'], 'longitude':data['longitude'], 'address':data['address'], 'city':data['city'], 'state':data['state']})
                        else:
                            for res in restaurants:
                                if res['id'] == data['restaurant']:
                                    res['restaurant_addresses'].append({'id':data['id'],'latitude':data['latitude'], 'longitude':data['longitude'], 'address':data['address'], 'city':data['city'], 'state':data['state']})
                page = self.paginate_queryset(restaurants)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(restaurants)
                serializer = self.get_serializer(restaurants, many=True)
                return Response(restaurants)
        response = super().list(request, *args, **kwargs)
        for restaurant in response.data['results']:
            if restaurant['menus']:
                restaurant['menus'] = sorted(restaurant['menus'], key=lambda x: x['menu_category']
                                             ['order'] if 'menu_category' in x and x['menu_category'] else -1)
        return response


class RestaurantDetailApi(generics.RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response({'error': {"restaurant_id": ["Please provide valid restaurant id."]}}, status=400)


class FavouriteMenuItemApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MenuItemSerlizers

    def get_queryset(self):
        favourite_menu_items_ids = self.request.user.favourite_menu_items.all().values_list('id',
                                                                                            flat=True)

        return MenuItem.objects.filter(id__in=favourite_menu_items_ids)


class FavouriteRestaurantApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        favourite_restaurant_ids = self.request.user.favourite_restaurants.all().values_list('id',
                                                                                             flat=True)
        return Restaurant.objects.filter(id__in=favourite_restaurant_ids)


class FavouriteAddRemoveApi(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, model_name, pk, format=None):
        is_favourite = request.GET.get('is_favourite')
        user = self.request.user
        if model_name == 'restaurants':
            if not Restaurant.objects.filter(pk=pk).exists():
                return Response({'error': {"restaurant_id": ["Please provide valid restaurant id."]}}, status=400)

            user.favourite_restaurants.add(
                pk) if is_favourite == 'true' else user.favourite_restaurants.remove(pk)
            restaurant = Restaurant.objects.get(pk=pk)
            serializer = RestaurantSerializer(restaurant)
            restaurant_id = pk
        elif model_name == 'menu-item':
            if not MenuItem.objects.filter(pk=pk).exists():
                return Response({'error': {"menu_item_id": ["Please provide valid menu item id."]}}, status=400)

            user.favourite_menu_items.add(
                pk) if is_favourite == 'true' else user.favourite_menu_items.remove(pk)
            menuitem = MenuItem.objects.get(pk=pk)
            serializer = MenuItemSerlizers(menuitem)
            restaurant_id = menuitem.restaurant.id
        return Response({'status': True, 'id': pk, 'is_favourite': is_favourite, 'restaurant_id': restaurant_id, 'favourite_item': serializer.data})


class SaveAddRemoveApi(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, format=None):
        is_save = request.GET.get('is_save')
        user = self.request.user
        if not MenuItem.objects.filter(pk=pk).exists():
            return Response({'error': {"menu_item_id": ["Please provide valid menu item id."]}}, status=400)

        get_user = User.objects.filter(id=user.id, provider_type='guest')

        if get_user.exists():
            return Response({'error': {"message": ["This user is guest user..!!"]}}, status=403)

        if is_save == 'true':
            SaveMenuItem.objects.get_or_create(
                user_id=user.id, menu_item_id=pk)
        else:
            SaveMenuItem.objects.filter(
                user_id=user.id, menu_item_id=pk).delete()
        menuitem = MenuItem.objects.get(pk=pk)
        serializer = MenuItemSerlizers(menuitem)
        restaurant_id = menuitem.restaurant.id
        return Response({'status': True, 'id': pk, 'is_save': is_save, 'restaurant_id': restaurant_id, 'save_item': serializer.data})


class SaveMenuItemApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaveMenuItemSerlizers
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['created_at', ]
    ordering_fields = ['created_at', 'menu_item__name',
                       'menu_item__restaurant__name']

    def get_queryset(self):
        return SaveMenuItem.objects.filter(user=self.request.user)


def total_data(request):
    data = {
        'total_users': User.objects.all().count(),
        'total_saves': MenuItem.objects.all().aggregate(Sum('total_saves'))['total_saves__sum'],
        'total_favourites':  MenuItem.objects.all().aggregate(Sum('total_favourites'))['total_favourites__sum'],
    }

    return JsonResponse(data)


class ReportSearchTextAPI(generics.CreateAPIView):
    serializer_class = ReportSearchTextSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)
        serializer.save()
        return Response({"message": [f"Report search text saved successfully"]}, status=200)
