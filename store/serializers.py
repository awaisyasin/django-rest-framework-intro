from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'sale_start', 'sale_end')
        filter_backends = (DjangoFilterBackend,)
        filter_fields = ('id',)

    def to_representation(self, instance):
        data =  super().to_representation(instance)
        data['is_on_salse'] = instance.is_on_sale()
        data['current_price'] = instance.current_price()
        return data