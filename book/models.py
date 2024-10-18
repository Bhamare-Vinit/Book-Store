from django.db import models
from django.conf import settings

class Book(models.Model):
    name = models.CharField(max_length=255, null=False, db_index=True,unique=True)
    author = models.CharField(max_length=255, null=False, db_index=True)
    description = models.TextField(null=True, blank=True)
    price = models.PositiveIntegerField(null=False, db_index=True)
    stock=models.PositiveIntegerField(null=False, default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book')

    class Meta:
        db_table = 'book'
# Create your models here.
