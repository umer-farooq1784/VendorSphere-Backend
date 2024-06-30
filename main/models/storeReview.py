from django.db import models
from main.models import NormalUser, Store

class StoreReview(models.Model):
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.DecimalField(
        blank=True, null=True, max_digits=2, decimal_places=1, default=0.0
    ) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.name}"
