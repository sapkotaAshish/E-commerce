import django_filters
from django_filters import NumberFilter
from django.db.models import Max, Avg, Min
from django_filters.filters import CharFilter
from .models import *


class ProductFilter(django_filters.FilterSet):
    price = NumberFilter(field_name = "price", lookup_expr='gte')
    price1 = NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['image','digital']
