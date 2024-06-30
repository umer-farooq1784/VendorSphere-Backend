from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import ProductReview
from main.models import Product
from main.models import StoreReview
from main.models import Store
from django.db.models import Avg


def update_product_rating(sender, instance, created, **kwargs):
    """
    Signal receiver function that updates the aggregate rating of the associated Product
    whenever a new ProductReview instance is created or updated.
    """
    if created:  # Only update the product's rating if a new review was created
        product = instance.product
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
        product.rating = avg_rating if avg_rating is not None else 0.0
        product.save()

# Register the signal
post_save.connect(update_product_rating, sender=ProductReview)


def update_store_rating(sender, instance, created, **kwargs):
    """
    Signal receiver function that updates the aggregate rating of the associated Store
    whenever a new StoreReview instance is created or updated.
    """
    if created:  # Only update the store's rating if a new review was created
        store = instance.store
        avg_rating = store.reviews.aggregate(Avg('rating'))['rating__avg']
        store.rating = avg_rating if avg_rating is not None else 0.0
        store.save()

# Register the signal
post_save.connect(update_store_rating, sender=StoreReview)