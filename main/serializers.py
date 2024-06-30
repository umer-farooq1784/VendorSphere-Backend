from rest_framework import serializers
from . import models

# pylint: disable=no-member


class NormalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NormalUser
        fields = ["user", "address", "role", "image"]

    def __init__(self, *args, **kwargs):
        super(NormalUserSerializer, self).__init__(*args, **kwargs)
        self.Meta.depth = 1


class NormalUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NormalUser
        fields = ["user", "address", "phone", "image", "email", "role", "subscription"]

    def __init__(self, *args, **kwargs):
        super(NormalUserDetailSerializer, self).__init__(*args, **kwargs)
        self.Meta.depth = 1


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImage
        fields = ["id", "image"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductCategory.objects.all()
    )
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = [
            "name",
            "id",
            "rating",
            "description",
            "price",
            "images",
            "owner",
            "category",
            "reviews",
            "is_featured",
        ]

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        return ProductReviewSerializer(reviews, many=True).data


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductCategory.objects.all()
    )
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = [
            "id",
            "name",
            "price",
            "images",
            "category",
            "vendor",
            "description",
            "reviews",
            "is_featured",
        ]

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        return ProductReviewSerializer(reviews, many=True).data


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductCategory
        fields = ["id", "name", "description", "created_at", "updated_at"]


class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=models.NormalUser.objects.all())

    class Meta:
        model = models.ProductReview
        fields = ["id", "user", "title", "content", "rating", "created_at"]


class StoreImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StoreImage
        fields = ["id", "image", "uploaded_at"]


class StoreReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=models.NormalUser.objects.all())

    class Meta:
        model = models.StoreReview
        fields = ["id", "user", "title", "content", "rating", "created_at"]


class StoreSerializer(serializers.ModelSerializer):
    images = StoreImageSerializer(many=True, read_only=True)
    reviews = StoreReviewSerializer(many=True, read_only=True)

    class Meta:
        model = models.Store
        fields = [
            "id",
            "owner",
            "name",
            "rating",
            "description",
            "location",
            "website",
            "product_category",
            "images",
            "reviews",
            "is_featured",
        ]


class ContractSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source="seller.name", read_only=True)
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    images = serializers.SerializerMethodField()  # Custom field for images

    def get_images(self, obj):
        if obj.request_source == 'Product':
            # Fetch and return images of the product
            product_images = models.ProductImage.objects.filter(product=obj.product)
            return ProductImageSerializer(product_images, many=True).data
        elif obj.request_source == 'Store':
            # Fetch and return images of the store
            store_images = models.StoreImage.objects.filter(store=obj.store)
            return StoreImageSerializer(store_images, many=True).data
        else:
            return []

    class Meta:
        model = models.Contract
        fields = [
            "id",
            "seller_name",
            "vendor_name",
            "product_name",
            "store_name",
            "product_quantity",
            "price_per_item",
            "commission_percentage",
            "request_source",
            "duration",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "seller",
            "vendor",
            "product",
            "store",
            "images"  # Include the images field
        ]


class StoreDetailSerializer(serializers.ModelSerializer):
    images = StoreImageSerializer(many=True, read_only=True)
    reviews = StoreReviewSerializer(many=True, read_only=True)
    product_category = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductCategory.objects.all()
    )

    class Meta:
        model = models.Store
        fields = [
            "id",
            "owner",
            "name",
            "description",
            "location",
            "website",
            "product_category",
            "images",
            "reviews",
            "is_featured",  # Add the is_featured field here
        ]


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product_id.name", read_only=True)
    vendor_name = serializers.CharField(source="contract_id.vendor.name", read_only=True)
    price_per_item = serializers.DecimalField(
        source="contract_id.price_per_item",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    commission_percentage = serializers.DecimalField(
        source="contract_id.commission_percentage",
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    start_date = serializers.DateTimeField(
        source="contract_id.start_date", read_only=True
    )
    end_date = serializers.DateTimeField(source="contract_id.end_date", read_only=True)
    store_name = serializers.CharField(source="store_id.name", read_only=True)

    class Meta:
        model = models.Inventory
        fields = [
            "id",
            "store_id",
            "product_id",
            "contract_id",
            "total_quantity",
            "available_quantity",
            "product_name",
            "vendor_name",
            "price_per_item",
            "commission_percentage",
            "start_date",
            "end_date",
            "store_name",
            "revenue",
            "quantity_sold",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "product_name",
            "vendor_name",
            "price_per_item",
            "commission_percentage",
            "start_date",
            "end_date",
            "store_name",
            "created_at",
            "updated_at",
        ]

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sale
        fields = "__all__"


class ReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Return
        fields = "__all__"