from django.db import models
from django.contrib.auth.models import User
from .subscription import Subscription
from .role import Role
# pylint: disable=no-member

def upload_to(instance, filename):
    return f"users/{filename}"

class NormalUser(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    image = models.ImageField(upload_to=upload_to, default="users/default.svg", null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_disabled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.subscription:
            default_subscription = Subscription.objects.get(name='Free')
            self.subscription = default_subscription
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username if self.user else self.email
