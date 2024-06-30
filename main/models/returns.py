from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

#pylint: disable=no-member

class Return(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(
        'Store',
        related_name='returns',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'Product',
        related_name='returns',
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    contract = models.ForeignKey(
        'Contract',
        related_name='returns',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Return {self.id} - Seller: {self.seller.id}, Product: {self.product.id}, Quantity: {self.quantity}"