from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'name', 'author', 'description', 'price','stock'
        ]
        read_only_fields = ('user',)