from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from main.models import Store, StoreImage
from main.models import ProductCategory
from main.models import NormalUser
from main.serializers import StoreSerializer
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from main.serializers import StoreReviewSerializer
from django.views.decorators.http import require_POST, require_GET
from rest_framework import status
import json
from rest_framework.decorators import api_view
from main.models import StoreReview
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# pylint: disable=no-member


# pylint: disable=no-member


@csrf_exempt
@require_POST
def add_store_review(request, store_id):
    try:
        store = Store.objects.get(pk=store_id)
    except Store.DoesNotExist:
        return JsonResponse(
            {"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_id = data.get("user")
        if user_id is None:
            raise ValueError("User ID is required")
        if not isinstance(user_id, int):
            raise ValueError("Invalid user ID format")
        user = NormalUser.objects.get(id=user_id)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON format in request body"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except ValueError:
        return JsonResponse(
            {"error": "Invalid user ID format or missing user ID in request body"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except NormalUser.DoesNotExist:
        return JsonResponse(
            {"error": "User with the provided ID does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = StoreReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save(
            store=store, user=user
        )  # Save the review with the retrieved user object
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@require_GET
def get_store_reviews(request, store_id):
    try:
        store = Store.objects.get(pk=store_id)
    except Store.DoesNotExist:
        return JsonResponse({"error": "Store not found"}, status=404)

    reviews = store.reviews.select_related("user")
    serialized_reviews = []
    for review in reviews:
        serialized_review = {
            "id": review.id,
            "user": {
                "id": review.user.id,
                "name": review.user.name,
                # Assuming NormalUser model has 'phone', 'address', 'city' attributes
                "phone": review.user.phone,
                "address": review.user.address,
                "city": review.user.city,
                # Assuming NormalUser model has 'image' attribute
                "image": review.user.image.url if review.user.image else None,
            },
            "title": review.title,
            "content": review.content,
            "rating": str(
                review.rating
            ),  # Convert DecimalField to string for JSON serialization
            "created_at": review.created_at,
        }
        serialized_reviews.append(serialized_review)

    return JsonResponse(serialized_reviews, safe=False)


@csrf_exempt
def add_store(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        location = request.POST.get("location")
        category_name = request.POST.get("category")  # Get category name
        images = request.FILES.getlist("images")
        user_id = request.POST.get("user_id")

        # Query the database for the category based on the name
        try:
            product_category = ProductCategory.objects.get(name=category_name)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Category does not exist"}, status=404)

        # Fetch the NormalUser instance based on the provided user ID
        try:
            user_id = int(user_id)
        except ValueError:
            return JsonResponse({"error": "Invalid user ID"}, status=400)

        # Fetch the NormalUser instance based on the provided user ID
        try:
            owner = NormalUser.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "User does not exist"}, status=404)

        # Create the store with the obtained product category and owner
        try:
            store = Store.objects.create(
                name=name,
                owner=owner,
                description=description,
                location=location,
                product_category=product_category,
            )
        except ValidationError as e:
            return JsonResponse({"error": e.message}, status=400)

        # Create store images
        for image in images:
            StoreImage.objects.create(store=store, image=image)

        return JsonResponse({"message": "Store added successfully"})
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


@csrf_exempt
def searchStores(request):
    if request.method == "GET":
        # Extract parameters from the request's query parameters
        search_query = request.GET.get("name", "")
        page_number = int(request.GET.get("page", 1))

        if not search_query:
            return JsonResponse({"error": "Please provide a search query"}, status=400)

        # Search for similar stores based on name or category
        similar_stores = Store.objects.filter(
            Q(name__icontains=search_query)
            | Q(product_category__name__icontains=search_query)
        )

        if not similar_stores.exists():
            return JsonResponse({"message": "No stores found"}, status=404)

        paginator = Paginator(similar_stores, 10)
        try:
            page_stores = paginator.page(page_number)
        except (EmptyPage, PageNotAnInteger):
            return JsonResponse(
                {"message": "No stores found for this page"}, status=404
            )

        serialized_stores = []
        for store in page_stores:
            serialized_store = {
                "id": store.id,
                "name": store.name,
                "description": store.description,
                "location": store.location,
                "rating": store.rating,
                "is_featured": store.is_featured,
                "ProductCategory": {
                    "id": store.product_category.id,
                    "name": store.product_category.name,
                    "description": store.product_category.description,
                    "created_at": store.product_category.created_at,
                    "updated_at": store.product_category.updated_at,
                },
                "ProductImages": [
                    {
                        "id": image.id,
                        "image_url": image.image.url,
                        "uploaded_at": image.uploaded_at,
                    }
                    for image in store.images.all()
                ],
                "NormalUser": {
                    "id": store.owner.id if store.owner else None,
                    "name": store.owner.name if store.owner else None,
                    "email": store.owner.email if store.owner else None,
                    "phone": store.owner.phone if store.owner else None,
                    "address": store.owner.address if store.owner else None,
                    "city": store.owner.city if store.owner else None,
                    "image": (
                        store.owner.image.url
                        if store.owner and store.owner.image
                        else None
                    ),
                },
            }
            serialized_stores.append(serialized_store)

        return JsonResponse({"similar_stores": serialized_stores})

    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


@csrf_exempt
def my_store_catalog(request, user_id):
    if request.method == "GET":
        try:
            user = NormalUser.objects.get(pk=user_id)
        except NormalUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        stores = Store.objects.filter(owner=user)
        serialized_stores = []
        for store in stores:
            serialized_store = {
                "id": store.id,
                "name": store.name,
                "description": store.description,
                "location": store.location,
                "is_featured": store.is_featured,
                "rating": store.rating,
                "ProductCategory": {
                    "id": store.product_category.id,
                    "name": store.product_category.name,
                    "description": store.product_category.description,
                    "created_at": store.product_category.created_at,
                    "updated_at": store.product_category.updated_at,
                },
                "ProductImages": [
                    {
                        "id": image.id,
                        "image_url": image.image.url,
                        "uploaded_at": image.uploaded_at,
                    }
                    for image in store.images.all()
                ],
                "NormalUser": {
                    "id": store.owner.id if store.owner else None,
                    "name": store.owner.name if store.owner else None,
                    "email": store.owner.email if store.owner else None,
                    "phone": store.owner.phone if store.owner else None,
                    "address": store.owner.address if store.owner else None,
                    "city": store.owner.city if store.owner else None,
                    "image": (
                        store.owner.image.url
                        if store.owner and store.owner.image
                        else None
                    ),
                },
            }
            serialized_stores.append(serialized_store)

        return JsonResponse({"stores": serialized_stores})


class StoreList(generics.ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class StoreDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


@require_http_methods(["GET"])
def get_top_stores(request):
    stores = Store.objects.order_by("-created_at")[:10]
    results = []
    for store in stores:
        store_data = {
            "id": store.id,
            "name": store.name,
            "description": store.description,
            "location": store.location,
            "website": store.website,
            "created_at": store.created_at,
            "updated_at": store.updated_at,
            "rating": store.rating,
            "is_featured": store.is_featured,
            "ProductImages": [
                {
                    "id": image.id,
                    "image_url": image.image.url,
                    "uploaded_at": image.uploaded_at,
                }
                for image in store.images.all()
            ],
            "ProductCategory": {
                "id": store.product_category.id if store.product_category else None,
                "name": store.product_category.name if store.product_category else None,
                "description": (
                    store.product_category.description
                    if store.product_category
                    else None
                ),
                "created_at": (
                    store.product_category.created_at
                    if store.product_category
                    else None
                ),
                "updated_at": (
                    store.product_category.updated_at
                    if store.product_category
                    else None
                ),
            },
        }
        results.append(store_data)
    return JsonResponse({"results": results})


@csrf_exempt
def get_store_details(request, store_id):
    if request.method == "GET":
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return JsonResponse({"error": "Store not found"}, status=404)

        serialized_store = {
            "id": store.id,
            "name": store.name,
            "description": store.description,
            "location": store.location,
            "rating": store.rating,
            "is_featured": store.is_featured,
            "ProductCategory": {
                "id": store.product_category.id,
                "name": store.product_category.name,
                "description": store.product_category.description,
                "created_at": store.product_category.created_at,
                "updated_at": store.product_category.updated_at,
            },
            "ProductImages": [
                {
                    "id": image.id,
                    "image_url": image.image.url,
                    "uploaded_at": image.uploaded_at,
                }
                for image in store.images.all()
            ],
            "NormalUser": {
                "id": store.owner.id if store.owner else None,
                "name": store.owner.name if store.owner else None,
                "email": store.owner.email if store.owner else None,
                "phone": store.owner.phone if store.owner else None,
                "address": store.owner.address if store.owner else None,
                "city": store.owner.city if store.owner else None,
                "image": (
                    store.owner.image.url if store.owner and store.owner.image else None
                ),
            },
        }
        return JsonResponse(serialized_store)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


@require_POST
def feature_store(request, store_id):
    try:
        store = Store.objects.get(pk=store_id)
    except Store.DoesNotExist:
        return JsonResponse(
            {"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND
        )

    store.is_featured = (
        True  # Assuming you have an `is_featured` field in your Store model
    )
    store.save()

    return JsonResponse(
        {"message": "Store featured successfully"}, status=status.HTTP_200_OK
    )


@csrf_exempt
@permission_classes([AllowAny])
@require_http_methods(["PUT", "DELETE"])
def update_store(request, store_id):
    try:
        store = Store.objects.get(pk=store_id)
    except Store.DoesNotExist:
        return JsonResponse({"error": "Store not found"}, status=404)

    if request.method == "PUT":
        data = json.loads(request.body.decode("utf-8"))

        # Update description, location, and name if provided in the request
        store.description = data.get("description", store.description)
        store.location = data.get("location", store.location)
        store.name = data.get("name", store.name)

        store.save()  # Save the store object after updating its fields

        # Check if images are provided in the request and update them
        if "images" in request.FILES:
            for image in request.FILES.getlist("images"):
                StoreImage.objects.create(store=store, image=image)

        return JsonResponse({"message": "Store updated successfully"})

    elif request.method == "DELETE":
        store.delete()
        return JsonResponse({"message": "Store deleted successfully"})

    else:
        return JsonResponse(
            {"error": "Only PUT and DELETE requests are allowed"}, status=405
        )


@require_GET
def get_featured_stores(request):
    featured_stores = Store.objects.filter(is_featured=True)
    serializer = StoreSerializer(featured_stores, many=True)
    return JsonResponse(serializer.data, safe=False)




def Setfeature_store(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            body_data = json.loads(data['body'])
            store_id = body_data.get("storeId")

            if not store_id:
                return JsonResponse({'status': 'error', 'message': 'storeId is required.'}, status=400)

            store = get_object_or_404(Store, id=store_id)
            store.is_featured = True
            store.save()
            print(f"Store {store_id} is now featured.")
            return JsonResponse({'status': 'success', 'message': 'Store is now featured.'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)
        except Store.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Store not found.'}, status=404)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method.'}, status=405)