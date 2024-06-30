from django.db import models
from django.db.models import Avg
from django.utils import timezone
#pylint: disable=no-member

def upload_to(instance, filename):
    return f"products/{instance.product.name}/{filename}"


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        "NormalUser",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.DecimalField(
        blank=True, null=True, max_digits=2, decimal_places=1, default=0.0
    )
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)  # New field
    category = models.ForeignKey(
        "ProductCategory", blank=True, on_delete=models.SET_NULL, null=True
    )

    def calculate_rating(self):
        reviews = self.reviews.all()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        return avg_rating if avg_rating is not None else 0.0

    def save(self, *args, **kwargs):
        if self.is_featured and not self.featured_until:
            self.featured_until = timezone.now() + timezone.timedelta(days=7)  # Assuming featured for 7 days
        # Call the original save method to perform the actual save operation
        super().save(*args, **kwargs)
        # Calculate and update the rating after the instance has been saved
        self.rating = self.calculate_rating()
        super().save(update_fields=['rating'])  # Save again to update only the 'rating' field

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.name)



class ProductCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        default="products/default.jpg",
    )
    image = models.ImageField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]
