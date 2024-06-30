from django.test import TestCase
from main.models import Product, NormalUser, ProductCategory, Subscription, Role
from django.contrib.auth.models import User

# pylint: disable=no-member

class ProductModelTest(TestCase):
    def setUp(self):
        self.subscription = Subscription.objects.create(name="Free", price=0.00, tier=1, description="Free tier")
        self.role = Role.objects.create(name="Customer", description="Customer role")
        self.user = NormalUser.objects.create(name="Test User", email="test@example.com", password="password")
        self.category = ProductCategory.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", 
            description="Test Description", 
            price=9.99, 
            owner=self.user,
            category=self.category
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.description, "Test Description")
        self.assertEqual(self.product.price, 9.99)
        self.assertEqual(self.product.owner, self.user)
        self.assertEqual(self.product.category, self.category)

    def test_product_delete(self):
        self.product.delete()
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=self.product.id)

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")

    def test_product_update(self):
        self.product.name = "Updated Product"
        self.product.save()
        self.assertEqual(self.product.name, "Updated Product")
