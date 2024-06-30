from django.db import models
from django.utils import timezone
from datetime import timedelta

class Contract(models.Model):
    STATUS_CHOICES = [
        ('Approved', 'Approved'),
        ('Pending', 'Pending'),
        ('Denied', 'Denied'),
    ]
    
    REQUEST_SOURCE_CHOICES = [
        ('Store', 'Store'),
        ('Product', 'Product'),
    ]

    id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(
        "NormalUser",
        related_name="seller_contracts",
        on_delete=models.CASCADE
    )
    vendor = models.ForeignKey(
        "NormalUser",
        related_name="vendor_contracts",
        on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        "Store",
        related_name="store_contracts",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE
    )
    product_quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    duration = models.IntegerField(default=0)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(editable=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    request_source = models.CharField(
        max_length=10,
        choices=REQUEST_SOURCE_CHOICES,
        default='Store'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.duration * 30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contract {self.id} - {self.seller} and {self.vendor} for {self.product}"

    class Meta:
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
