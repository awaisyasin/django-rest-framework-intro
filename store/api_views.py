from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .serializers import ProductSerializer, ProductStatSerializer
from .models import Product

class ProductPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filter_fields = ('id',)
    search_fields = ('name', 'description',)
    pagination_class = ProductPagination

    def get_queryset(self):
        on_sale = self.request.query_params.get('on_sale', None)
        if on_sale is None:
            return super().get_queryset()
        queryset = Product.objects.all()
        if on_sale.lower() == "true":
            from django.utils import timezone
            now = timezone.now()
            return queryset.filter(
                sale_start__lte = now,
                sale_end__gte = now,
            )

        return super().get_queryset()

class ProductCreate(CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        try:
            price = request.data.get('price')
            if price is not None and float(price) <= 0.0:
                raise ValidationError({'price' : 'Must be above $0.00'})
        except ValueError:
            raise ValidationError({'price' : 'Required a valid number'})

        return super().create(request, *args, **kwargs)

class ProductRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'
    serializer_class = ProductSerializer

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('id')
        response =  super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            from django.core.cache import cache
            cache.delete(f'product_data_{product_id}')

        return response

    def update(self, request, *args, **kwargs):
        response =  super().update(request, *args, **kwargs)
        if response.status_code == 204:
            from django.core.cache import cache
            product = response.data
            cache.set(f'product_data_{product["id"]}', {
                'name': product['name'],
                'description' : product['description'],
                'price' : product['price'],
            })

        return response

class ProductStats(GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductStatSerializer
    lookup_field = 'id'

    def get(self, request, format=None, id=None):
        obj = self.get_object()
        serializer = ProductStatSerializer({
            'stats' : {
                '2019-01-01' : [5, 10, 2],
                '2019-01-02' : [2, 15, 8],
            }
        })
        return Response(serializer.data)