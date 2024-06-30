from django.db import models
from main.models import Product

class ProductReview(models.Model):
    user = models.ForeignKey(
        "NormalUser",  # Assuming "NormalUser" is the name of your custom user model
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.IntegerField(default=0)  # You can adjust this according to your rating system
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.name}"
