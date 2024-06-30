from django.test import TestCase
from main.models import Store, NormalUser, ProductCategory, Subscription, Role
from django.contrib.auth.models import User
# pylint: disable=no-member

class StoreModelTest(TestCase):
    def setUp(self):
        self.subscription = Subscription.objects.create(name="Free", price=0.00, tier=1, description="Free tier")
        self.role = Role.objects.create(name="Customer", description="Customer role")
        self.user1 = User.objects.create_user(username="test_user", email="test@example.com", password="password")
        self.user = NormalUser.objects.create(user=self.user1, name="Test User", email="test@example.com", password="password", subscription=self.subscription, role=self.role)
        self.category = ProductCategory.objects.create(name="Test Category", description="Test Description")
        self.store = Store.objects.create(name="Test Store", location="123 Test St", owner=self.user, product_category=self.category)

    def test_store_creation(self):
        self.assertEqual(self.store.name, "Test Store")
        self.assertEqual(self.store.location, "123 Test St")
        self.assertEqual(self.store.owner, self.user)
        self.assertEqual(self.store.product_category, self.category)

    def test_store_str(self):
        self.assertEqual(str(self.store), "Test Store")

    def test_store_update(self):
        self.store.name = "Updated Store"
        self.store.save()
        self.assertEqual(self.store.name, "Updated Store")

    def test_store_delete(self):
        store_id = self.store.id
        self.store.delete()
        with self.assertRaises(Store.DoesNotExist):
            Store.objects.get(id=store_id)