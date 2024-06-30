from django.db import models
from django.db.models import Avg

# pylint: disable=no-member


def upload_to(instance, filename):
    return f"store/{instance.store.name}/{filename}"


class Store(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        "NormalUser",
        on_delete=models.CASCADE,
        related_name="stores",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=200)
    website = models.URLField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product_category = models.ForeignKey(
        "ProductCategory", on_delete=models.SET_NULL, null=True
    )
    is_featured = models.BooleanField(default=False)
    rating = models.DecimalField(
        blank=True, null=True, max_digits=2, decimal_places=1, default=0.0
    )

    def calculate_rating(self):
        reviews = self.reviews.all()
        avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"]
        return avg_rating if avg_rating is not None else 0.0

    def save(self, *args, **kwargs):
        # Call the original save method to perform the actual save operation
        super().save(*args, **kwargs)
        # Calculate and update the rating after the instance has been saved
        self.rating = self.calculate_rating()
        super().save(
            update_fields=["rating"]
        )  # Save again to update only the 'rating' field

    def __str__(self):
        return str(self.name)


class StoreImage(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]
