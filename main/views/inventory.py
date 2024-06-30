# views.py
from django.http import JsonResponse
from django.db.models import Q, F
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from main.models import Inventory, Store, Product, Contract, Sale, Return
from main.serializers import InventorySerializer, SaleSerializer

#pylint: disable=no-member
# 1. Get all inventory items where either I'm the store owner, or I'm the product owner
@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_inventory(request, user_id):
    try:
        inventories = Inventory.objects.filter(
            Q(store_id__owner_id=user_id) | Q(product_id__owner_id=user_id)
        ).annotate(
            store_name=F('store_id__name')
        )
        serializer = InventorySerializer(inventories, many=True)
        inventory_data = serializer.data

        for item in inventory_data:
            item['store_name'] = inventories.get(id=item['id']).store_name

        return JsonResponse(inventory_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

# 2. Get detail of an inventory item given its ID
@api_view(['GET'])
@permission_classes([AllowAny])
def inventory_detail(request, inventory_id):
    try:
        inventory = Inventory.objects.get(pk=inventory_id)
        serializer = InventorySerializer(inventory)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Inventory.DoesNotExist:
        return JsonResponse({'error': 'Inventory item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

# 3. Decrement the quantity of items and create a sales entry automatically
@api_view(['POST'])
@permission_classes([AllowAny])
def decrement_inventory(request, inventory_id):
    try:
        data = request.data
        quantity_to_decrement = data.get('quantity')

        if quantity_to_decrement is None or int(quantity_to_decrement) <= 0:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        inventory = Inventory.objects.get(pk=inventory_id)
        
        if inventory.available_quantity < int(quantity_to_decrement):
            return JsonResponse({'error': 'Not enough available quantity'}, status=400)
        
        inventory.available_quantity -= int(quantity_to_decrement)
        inventory.quantity_sold += int(quantity_to_decrement)
        inventory.revenue = inventory.contract_id.price_per_item * int(quantity_to_decrement)
        inventory.save()

        # Create a sale entry
        sale = Sale(
            store=inventory.store_id,
            product=inventory.product_id,
            quantity=int(quantity_to_decrement),
            contract=inventory.contract_id,
            price=inventory.product_id.price * int(quantity_to_decrement),
            date=timezone.now()
        )
        sale.save()

        serializer = SaleSerializer(sale)
        return JsonResponse(serializer.data, status=201)
    except Inventory.DoesNotExist:
        return JsonResponse({'error': 'Inventory item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def increment_inventory(request, inventory_id):
    try:
        data = request.data
        quantity_to_increment = data.get('quantity')


        # Check if the quantity is provided and is not None
        if quantity_to_increment is None:
            return JsonResponse({'error': 'Quantity is missing'}, status=400)

        # Attempt to strip spaces (if it's a string) and convert to integer
        try:
            if isinstance(quantity_to_increment, str):
                quantity_to_increment = int(quantity_to_increment.strip())
            else:
                quantity_to_increment = int(quantity_to_increment)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity format'}, status=400)

        if quantity_to_increment <= 0:
            return JsonResponse({'error': 'Quantity must be a positive integer'}, status=400)

        inventory = Inventory.objects.get(pk=inventory_id)
        if inventory.total_quantity < inventory.available_quantity + quantity_to_increment:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        inventory.available_quantity += quantity_to_increment
        inventory.quantity_sold -= quantity_to_increment
        inventory.revenue = inventory.contract_id.price_per_item * inventory.quantity_sold
        inventory.save()

        returned = Return(
            store=inventory.store_id,
            product=inventory.product_id,
            quantity=quantity_to_increment,
            contract=inventory.contract_id,
            price=inventory.product_id.price * quantity_to_increment,
            date=timezone.now()
        )

        returned.save()
        return JsonResponse({'message': 'Inventory incremented successfully'}, status=200)
    except Inventory.DoesNotExist:
        return JsonResponse({'error': 'Inventory item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {e}'}, status=500)