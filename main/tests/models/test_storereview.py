from django.test import TestCase
from main.models import StoreReview, NormalUser, Store, Subscription
from django.core.exceptions import ObjectDoesNotExist

#pylint: disable=no-member

class StoreReviewModelTest(TestCase):
    def setUp(self):
        # Create a Subscription instance
        self.subscription = Subscription.objects.create(name="Free", price=0.00, tier=1, description="Free tier")
        
        # Create a NormalUser instance
        self.user = NormalUser.objects.create(name="Test User", email="test@example.com", password="password", subscription=self.subscription)
        
        # Create a Store instance
        self.store = Store.objects.create(name="Test Store", location="Test Location")

    def test_review_creation(self):
        # Ensure that a StoreReview instance can be created
        review = StoreReview.objects.create(
            user=self.user,
            store_id=self.store.id,  # Use store id here
            title="Test Review",
            content="This is a test review",
            rating=4.5
        )

        # Check if the review was created successfully
        self.assertIsNotNone(review)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.store_id, self.store.id)  # Check store id here
        self.assertEqual(review.title, "Test Review")
        self.assertEqual(review.content, "This is a test review")
        self.assertEqual(review.rating, 4.5)

    def test_review_str(self):
        # Create a StoreReview instance
        review = StoreReview.objects.create(
            user=self.user,
            store_id=self.store.id,  # Use store id here
            title="Test Review",
            content="This is a test review",
            rating=4.5
        )

        # Check if the __str__ method returns the expected string
        expected_str = f"Test Review - {self.user.name}"
        self.assertEqual(str(review), expected_str)

    