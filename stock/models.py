from django.utils import timezone

from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added = models.DateTimeField(auto_now_add=True)
    expiry = models.DateField()
    quantity = models.PositiveIntegerField()
    low_stock = models.PositiveIntegerField()

    @property
    def in_stock(self) -> bool:
        return self.quantity > 0

    @property
    def is_expired(self) -> bool:
        return self.expiry <= timezone.now()

    @property
    def days_remaining(self) -> int:
        return (self.expiry - timezone.now()).days

    def __str__(self):
        return self.name
