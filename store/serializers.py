from rest_framework import serializers

from .models import Product, ShoppingCartItem

class CartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, max_value=100)
    class Meta:
        model = ShoppingCartItem
        fields = ('product', 'quantity',)

class ProductSerializer(serializers.ModelSerializer):
    is_on_sale = serializers.BooleanField(read_only=True)
    current_price = serializers.FloatField(read_only=True)
    description = serializers.CharField(min_length=2, max_length=200)
    cart_items = serializers.SerializerMethodField()
    price = serializers.FloatField(min_value=1.00, max_value=100000)
    # price = serializers.DecimalField(
    #     max_digits = None,
    #     decimal_places = 2,
    #     min_value = 1.00,
    #     max_value = 100000
    # )
    sale_start = serializers.DateTimeField(
        format = None,
        input_formats = ['%I:%M %p %d %B %Y',],
        allow_null = True,
        style = {'input_type' : 'text', 'placeholder' : '02:39 PM 2 February 2024',},
        help_text = 'Accepted format is "02:39 PM 2 February 2024"',
    )
    sale_end = serializers.DateTimeField(
        format = None,
        input_formats = ['%I:%M %p %d %B %Y',],
        allow_null = True,
        style = {'input_type' : 'text', 'placeholder' : '02:39 PM 2 February 2024'},
        help_text = 'Accepted format is "02:39 PM 2 February 2024"',
    )
    photo = serializers.ImageField(default=None)
    warranty = serializers.FileField(write_only=True, default=None)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'sale_start', 'sale_end', 'is_on_sale', 'current_price', 'cart_items', 'photo', 'warranty',)

    def get_cart_items(self, instance):
        items = ShoppingCartItem.objects.filter(product=instance)
        return CartItemSerializer(items, many=True).data

    def update(self, instance, validated_data):
        if validated_data.get('warranty', None):
            instance.description += '\n\nWarranty Information:\n'
            instance.description += b'; '.join(
                validated_data['warranty'].readlines()
            ).decode()
        # return super().update(instance, validated_data)
            instance.save()
            return instance

class ProductStatSerializer(serializers.Serializer):
    stats = serializers.DictField(
        child = serializers.ListField(
            child = serializers.IntegerField(),
        )
    )