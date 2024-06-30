from django.test import TestCase
from django.contrib.auth.models import User
from main.models import NormalUser, Subscription, Role

# pylint: disable=no-member
class UserModelTest(TestCase):
    def setUp(self):
        self.subscription = Subscription.objects.create(name="Free", price=0.00, tier=1, description="Free tier")
        self.role = Role.objects.create(name="Customer", description="Customer role")
        self.user1 = User.objects.create_user(username='test_user', email='test@example.com', password='password')
        self.normal_user = NormalUser.objects.create(user=self.user1, name="Test User", email="test@example.com", password="password", subscription=self.subscription, role=self.role)

    def test_normal_user_creation(self):
        self.assertEqual(self.normal_user.name, "Test User")
        self.assertEqual(self.normal_user.email, "test@example.com")
        self.assertEqual(self.normal_user.subscription, self.subscription)
        self.assertEqual(self.normal_user.role, self.role)

    def test_normal_user_str(self):
        self.assertEqual(str(self.normal_user), "test_user")

    def test_normal_user_update(self):
        self.normal_user.name = "Updated User"
        self.normal_user.save()
        self.assertEqual(self.normal_user.name, "Updated User")

    def test_normal_user_delete(self):
        normal_user_id = self.normal_user.id
        self.normal_user.delete()
        with self.assertRaises(NormalUser.DoesNotExist):
            NormalUser.objects.get(id=normal_user_id)