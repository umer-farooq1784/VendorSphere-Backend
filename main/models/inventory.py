from django.db import models

class Inventory(models.Model):
    id = models.AutoField(primary_key=True)
    store_id = models.ForeignKey('Store', on_delete=models.CASCADE)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    contract_id = models.ForeignKey('Contract', on_delete=models.CASCADE)
    total_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField()
    quantity_sold = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)