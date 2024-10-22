from rest_framework import serializers
from .models import Cart, CartItem
from book.models import Book

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'book', 'quantity', 'price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'total_price', 'total_quantity', 'is_ordered', 'user', 'items']
        read_only_fields = ('user', 'total_price', 'total_quantity', 'is_ordered')
