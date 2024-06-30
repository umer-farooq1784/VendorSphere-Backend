from django.contrib import admin
from .models import user
from .models import store
from .models import product
from .models import subscription
from .models import transactions
from .models import role

# Register your models here.
admin.site.register(user.NormalUser)
admin.site.register(store.Store)
admin.site.register(product.Product)
admin.site.register(product.ProductCategory)
admin.site.register(subscription.Subscription)
admin.site.register(transactions.Transaction)
admin.site.register(role.Role)
