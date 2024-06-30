from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

class Sale(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(
        'Store',
        related_name='sales',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'Product',
        related_name='sales',
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    contract = models.ForeignKey(
        'Contract',
        related_name='sales',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale {self.id} - Seller: {self.seller.id}, Product: {self.product.id}, Quantity: {self.quantity}"



def calculate_sales(self):
        # Get the current date
        now = timezone.now()
        current_year = now.year
        previous_year = current_year - 1

        # Calculate start and end dates for the current year
        start_current_year = datetime(current_year, 1, 1)
        end_current_year = datetime(current_year, 12, 31, 23, 59, 59)

        # Calculate start and end dates for the previous year
        start_previous_year = datetime(previous_year, 1, 1)
        end_previous_year = datetime(previous_year, 12, 31, 23, 59, 59)

        # Calculate total sales for the current year
        current_year_sales = self.sales.filter(date__range=(start_current_year, end_current_year)).aggregate(total=Sum('price'))['total'] or 0

        # Calculate total sales for the previous year
        previous_year_sales = self.sales.filter(date__range=(start_previous_year, end_previous_year)).aggregate(total=Sum('price'))['total'] or 0

        return {
            'current_year_sales': current_year_sales,
            'previous_year_sales': previous_year_sales
        }



class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
