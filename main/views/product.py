from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from main.models import Product, ProductCategory, ProductImage
from main.serializers import ProductSerializer
from rest_framework import generics
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from main.models import NormalUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
import json
from django.views.decorators.http import require_POST, require_GET
from main.models import Store
from rest_framework import status
from main.serializers import ProductReviewSerializer
from django.contrib.auth.models import User 
from rest_framework.decorators import api_view
from main.models import ProductReview
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# pylint: disable=no-member

@csrf_exempt
@require_POST
def add_product_review(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        data = json.loads(request.body.decode('utf-8'))  
        user_id = data.get('user')
        if user_id is None:  
            raise ValueError("User ID is required")
        if not isinstance(user_id, int):  
            raise ValueError("Invalid user ID format")
        user = NormalUser.objects.get(id=user_id)  
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format in request body"}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return JsonResponse({"error": "Invalid user ID format or missing user ID in request body"}, status=status.HTTP_400_BAD_REQUEST)
    except NormalUser.DoesNotExist:
        return JsonResponse({"error": "User with the provided ID does not exist"}, status=status.HTTP_404_NOT_FOUND)

    
    serializer = ProductReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save(product=product, user=user)  # Save the review with the retrieved user object
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@require_GET
def get_product_reviews(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    reviews = ProductReview.objects.filter(product=product).select_related('user')
    serialized_reviews = []
    for review in reviews:
        serialized_review = {
            'id': review.id,
            'user': {
                'id': review.user.id,
                'name': review.user.name,
                'phone': review.user.phone,
                'address': review.user.address,
                'city': review.user.city,
                'image': review.user.image.url if review.user.image else None,
            },
            'title': review.title,
            'content': review.content,
            'rating': review.rating,
            'created_at': review.created_at,
        }
        serialized_reviews.append(serialized_review)

    return JsonResponse(serialized_reviews, safe=False)


@require_GET
def get_product_details(request, product_id):
    product = get_object_or_404(Product.objects.select_related('category', 'owner').prefetch_related('images'), pk=product_id)
    
    product_data = {
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'description': product.description,
        'rating': product.rating,
        'is_featured': product.is_featured,
        'ProductCategory': {
            'id': product.category.id,
            'name': product.category.name,
            'description': product.category.description,
            'created_at': product.category.created_at,
            'updated_at': product.category.updated_at,
        },
        'ProductImages': [
            {
                'id': image.id,
                'image_url': image.image.url,
                'uploaded_at': image.uploaded_at,
            }
            for image in product.images.all()
        ],
        'NormalUser': {
                'id': product.owner.id if product.owner else None,
                'email': product.owner.email if product.owner else None,
                'name': product.owner.name if product.owner else None,
                'phone': product.owner.phone if product.owner else None,
                'address': product.owner.address if product.owner else None,
                "city": product.owner.city if product.owner else None,
                "image": product.owner.image.url if product.owner and product.owner.image else None,
            },
    }

    return JsonResponse(product_data)  

@require_http_methods(["GET"])
def get_top_products(request):
    products = Product.objects.select_related('category', 'owner').prefetch_related('images').order_by('-created_at')[:10]
    results = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'rating': product.rating,
            'is_featured': product.is_featured,
            'ProductCategory': {
                'id': product.category.id,
                'name': product.category.name,
                'description': product.category.description,
                'created_at': product.category.created_at,
                'updated_at': product.category.updated_at,
            },
            'ProductImages': [
                {
                    'id': image.id,
                    'image_url': image.image.url,
                    'uploaded_at': image.uploaded_at,
                }
                for image in product.images.all()
            ],
           
            
        }
        results.append(product_data)
    return JsonResponse({'results': results})

@csrf_exempt
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        category_text = request.POST.get("category")
        images = request.FILES.getlist("images")
        user_id = request.POST.get("user_id")
        # Check if all required fields are present
        if not (name and description and price and category_text and images):
            return JsonResponse({"error": "All fields are required"}, status=400)


        # Query the database for the category ID based on the category text
        category = get_object_or_404(ProductCategory, name=category_text)
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

        # Create the product with the obtained category
        try:
            product = Product.objects.create(
                name=name,
                description=description,
                owner=owner,
                price=price,
                category=category,
            )
        except ValidationError as e:
            return JsonResponse({"error": e.message}, status=400)

        # Create product images
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return JsonResponse({"message": "Product added successfully"})
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


@csrf_exempt
@permission_classes([AllowAny])
@require_http_methods(["PUT", "DELETE"])
def update_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    if request.method == "PUT":
        data = json.loads(request.body.decode('utf-8'))

        # Update name, description, and price if provided in the request
        product.name = data.get("name", product.name) if data.get("name") else product.name
        product.description = data.get("description", product.description) if data.get("description") else product.description
        product.price = Decimal(data.get("price", product.price)) if data.get("price") else product.price

        product.save()

        # Check if images are provided in the request and update them
        if 'images' in request.FILES:
            for image in request.FILES.getlist("images"):
                ProductImage.objects.create(product=product, image=image)

        return JsonResponse({"message": "Product updated successfully"})

    elif request.method == "DELETE":
        product.delete()
        return JsonResponse({"message": "Product deleted successfully"})

    else:
        return JsonResponse({"error": "Only PUT and DELETE requests are allowed"}, status=405)


@csrf_exempt
def searchProducts(request):
    if request.method == "GET":
        # Extract parameters from the request's query parameters
        search_query = request.GET.get('name', '')
        page_number = int(request.GET.get('page', 1))

        if not search_query:
            return JsonResponse({'message': 'Please provide a search query'}, status=400)

        # Search for similar products based on name or category
        similar_products = Product.objects.filter(
            Q(name__icontains=search_query) | Q(category__name__icontains=search_query)
        )
        if not similar_products.exists():
            return JsonResponse({'message': 'No products found'}, status=404)
        
        # Pagination
        paginator = Paginator(similar_products, 10)  
        try:
            page_products = paginator.page(page_number)
        except EmptyPage:
            return JsonResponse({'message': 'No products found for this page'}, status=404)

        # Serialize the queryset of products for the current page
        serialized_products = []
        for product in page_products:
            serialized_product = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'rating': product.rating,
                'is_featured': product.is_featured,
                'ProductCategory': {
                    'id': product.category.id,
                    'name': product.category.name,
                    'description': product.category.description,
                    'created_at': product.category.created_at,
                    'updated_at': product.category.updated_at,
                },
                'ProductImages': [
                    {
                        'id': image.id,
                        'image_url': image.image.url,
                        'uploaded_at': image.uploaded_at,
                    }
                    for image in product.images.all()
                ],
            }
            serialized_products.append(serialized_product)

        return JsonResponse({'similar_products': serialized_products})

    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

  

@csrf_exempt
def my_product_catalog(request, user_id):
    if request.method == "GET":
        try:
            user = NormalUser.objects.get(id=user_id)
        except NormalUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        products = Product.objects.filter(owner=user)
        serialized_products = []
        for product in products:
            serialized_product = {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'description': product.description,
                'is_featured': product.is_featured,
                'rating': product.rating,
                'ProductCategory': {
                    'id': product.category.id,
                    'name': product.category.name,
                    'description': product.category.description,
                    'created_at': product.category.created_at,
                    'updated_at': product.category.updated_at,
                },
                'ProductImages': [
                    {
                        'id': image.id,
                        'image_url': image.image.url,
                        'uploaded_at': image.uploaded_at,
                    }
                    for image in product.images.all()
                ],
                
            }
            serialized_products.append(serialized_product)

        return JsonResponse({'products': serialized_products})

    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



@require_POST
def feature_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.is_featured = True
    product.save()
    return JsonResponse({"message": "Product marked as featured"}, status=status.HTTP_200_OK)

@require_GET
def get_featured_products(request):
    featured_products = Product.objects.filter(is_featured=True)
    serializer = ProductSerializer(featured_products, many=True)
    return JsonResponse(serializer.data, safe=False)


def Setfeature_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            data = json.loads(request.body)
            body_data = json.loads(data['body'])
            product_id = body_data.get("storeId")
            print(product_id)

            if not product_id:
                return JsonResponse({'status': 'error', 'message': 'productId is required.'}, status=400)

            product = get_object_or_404(Product, id=product_id)
            product.is_featured = True
            product.save()
            print(f"Product {product_id} is now featured.")
            return JsonResponse({'status': 'success', 'message': 'Product is now featured.'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found.'}, status=404)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method.'}, status=405)