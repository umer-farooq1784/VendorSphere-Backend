from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from main.models import Contract, NormalUser, Store, Product, ProductCategory, Subscription, Role

# pylint: disable=no-member

class ContractModelTest(TestCase):

    def setUp(self):
        # Create test instances of related models
        self.subscription = Subscription.objects.create(name='Free', price=0.00, tier=1, description="Free tier")
        self.role = Role.objects.create(name='Customer', description="Customer role")
        self.user1 = User.objects.create_user(username='seller_user', password='password')
        self.user2 = User.objects.create_user(username='vendor_user', password='password')
        self.seller = NormalUser.objects.create(user=self.user1, name="Seller", email="seller@example.com", password="password")
        self.vendor = NormalUser.objects.create(user=self.user2, name="Vendor", email="vendor@example.com", password="password")
        
        self.product_category = ProductCategory.objects.create(name="Electronics")
        self.store = Store.objects.create(
            owner=self.seller, 
            name="Test Store", 
            location="Test Location", 
            product_category=self.product_category
        )
        self.product = Product.objects.create(
            owner=self.seller, 
            name="Test Product", 
            price=100.00, 
            category=self.product_category
        )
        

    def test_create_contract(self):
        contract = Contract.objects.create(
            seller=self.seller,
            vendor=self.vendor,
            store=self.store,
            product=self.product,
            product_quantity=10,
            price_per_item=100.00,
            commission_percentage=5.00,
            duration=6  # 6 months
        )
        self.assertEqual(contract.seller, self.seller)
        self.assertEqual(contract.vendor, self.vendor)
        self.assertEqual(contract.store, self.store)
        self.assertEqual(contract.product, self.product)
        self.assertEqual(contract.product_quantity, 10)
        self.assertEqual(contract.price_per_item, 100.00)
        self.assertEqual(contract.commission_percentage, 5.00)
        self.assertEqual(contract.duration, 6)

    def test_end_date_calculation(self):
        start_date = timezone.now()
        duration = 6  # 6 months
        contract = Contract.objects.create(
            seller=self.seller,
            vendor=self.vendor,
            store=self.store,
            product=self.product,
            product_quantity=10,
            price_per_item=100.00,
            commission_percentage=5.00,
            duration=duration,
            start_date=start_date
        )
        expected_end_date = start_date + timedelta(days=duration * 30)
        self.assertEqual(contract.end_date, expected_end_date)

    def test_default_status(self):
        contract = Contract.objects.create(
            seller=self.seller,
            vendor=self.vendor,
            store=self.store,
            product=self.product,
            product_quantity=10,
            price_per_item=100.00,
            commission_percentage=5.00,
            duration=6
        )
        self.assertEqual(contract.status, 'Pending')

    def test_str_representation(self):
        contract = Contract.objects.create(
            seller=self.seller,
            vendor=self.vendor,
            store=self.store,
            product=self.product,
            product_quantity=10,
            price_per_item=100.00,
            commission_percentage=5.00,
            duration=6
        )
        expected_str = f"Contract {contract.id} - {contract.seller} and {contract.vendor} for {contract.product}"
        self.assertEqual(str(contract), expected_str)

    def test_save_method(self):
        contract = Contract(
            seller=self.seller,
            vendor=self.vendor,
            store=self.store,
            product=self.product,
            product_quantity=10,
            price_per_item=100.00,
            commission_percentage=5.00,
            duration=6
        )
        contract.save()
        expected_end_date = contract.start_date + timedelta(days=contract.duration * 30)
        self.assertEqual(contract.end_date, expected_end_date)
