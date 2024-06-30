# main/views/contract.py
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from main.models import Inventory, Store, Contract, NormalUser, Product
from main.serializers import InventorySerializer, ContractSerializer
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# pylint: disable=no-member

class StoreInventoryView(APIView):
    def get(self, request, store_id):
        try:
            store = Store.objects.get(pk=store_id)
            inventory = Inventory.objects.filter(store_id=store)
            serializer = InventorySerializer(inventory, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({'error': 'Store not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def send_contract_view(request):
    if request.method == 'POST':
        # Create a mutable copy of the request data
        data = request.data.copy()

        # Extract the product ID and store ID from the request data
        product_id = data.get('product_id')
        store_id = data.get('store_id')

        # Extract the source from the request data
        source = data.get('request_source')

        if not product_id or not store_id or not source:
            return Response({'error': 'Product ID, Store ID, and Source are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Query the product table to get the vendor ID
            product = Product.objects.get(id=product_id)
            vendor_id = product.owner.id

            # Query the store to get the seller ID
            store = Store.objects.get(id=store_id)
            seller_id = store.owner.id

            # Set the vendor, product, seller, and store IDs in the data
            data['vendor'] = vendor_id
            data['product'] = product_id
            data['seller'] = seller_id
            data['store'] = store_id

            # Set the source in the data
            data['request_source'] = source

            # Set the current date and time as start_date
            data['start_date'] = timezone.now()

            # Ensure end_date is correctly calculated
            duration = int(data.get('duration', 0))
            data['end_date'] = timezone.now() + timezone.timedelta(days=duration * 30)

            serializer = ContractSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Store.DoesNotExist:
            return Response({'error': 'Store does not exist'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def accept_contract_view(request):
    contract_id = request.data.get('contract_id')
    try:
        contract = Contract.objects.get(pk=contract_id)
        contract.status = 'Approved'
        contract.save()

        # Create inventory entry
        inventory_data = {
            'store_id': contract.store.id,
            'product_id': contract.product.id,
            'contract_id': contract.id,
            'total_quantity': contract.product_quantity,
            'available_quantity': contract.product_quantity
        }
        inventory_serializer = InventorySerializer(data=inventory_data)
        if inventory_serializer.is_valid():
            inventory_serializer.save()
            return Response({'status': 'Contract approved and inventory updated'}, status=status.HTTP_200_OK)
        return Response(inventory_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Contract.DoesNotExist:
        return Response({'error': 'Contract not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def reject_contract_view(request):
    contract_id = request.data.get('contract_id')
    try:
        contract = Contract.objects.get(pk=contract_id)
        contract.status = 'Denied'
        contract.save()

        # Delete the inventory record if it exists
        inventory = Inventory.objects.filter(contract_id=contract_id)
        if inventory.exists():
            inventory.delete()
            return Response({'status': 'Contract denied and inventory record deleted'}, status=status.HTTP_200_OK)

        return Response({'status': 'Contract denied'}, status=status.HTTP_200_OK)
    except Contract.DoesNotExist:
        return Response({'error': 'Contract not found'}, status=status.HTTP_404_NOT_FOUND)

class UserContractsView(APIView):
    def get(self, request, user_id):
        try:
            user = NormalUser.objects.get(pk=user_id)
            contracts = Contract.objects.filter(Q(seller=user) | Q(vendor=user))
            serializer = ContractSerializer(contracts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NormalUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class PendingContractsView(APIView):
    def get(self, request, user_id):
        try:
            user = NormalUser.objects.get(pk=user_id)
            pending_contracts = Contract.objects.filter(
                Q(seller=user) | Q(vendor=user),
                status='Pending'
            )
            serializer = ContractSerializer(pending_contracts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NormalUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@require_http_methods(["GET"])
@permission_classes([AllowAny])
def user_contracts_view(request, user_id):
    try:
        # Retrieve contracts where the user is either the seller or the vendor
        contracts = Contract.objects.filter(Q(seller_id=user_id) | Q(vendor_id=user_id))
        
        # Serialize the contract data
        serializer = ContractSerializer(contracts, many=True)
        
        # Return the serialized data in a JSON response
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        # Return an error response
        return JsonResponse({'error': 'An error occurred while retrieving contracts'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def single_contract_view(request, contract_id):
    try:
        contract = Contract.objects.get(pk=contract_id)
        serializer = ContractSerializer(contract)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Contract.DoesNotExist:
        return Response({'error': 'Contract not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_active_contracts(request, user_id):
    now = timezone.now()

    active_contracts_count = Contract.objects.filter(
        Q(vendor_id=user_id) | Q(seller_id=user_id),
        status='Approved',
        end_date__gte=now
    ).count()

    return JsonResponse({'active_contracts_count': active_contracts_count})


@csrf_exempt
@permission_classes([AllowAny])
@require_http_methods(["GET"])
def check_accepted_contract_product(request, product_id, user_id):
    try:
        has_contract = Contract.objects.filter(
            product_id=product_id,
            seller_id=user_id,
            status='Approved'
        ).exists()
        
        return JsonResponse({"has_accepted_contract": has_contract})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@permission_classes([AllowAny])
@require_http_methods(["GET"])
def check_accepted_contract_store(request, store_id, user_id):
    try:
        has_contract = Contract.objects.filter(
            store_id=store_id,
            vendor_id=user_id,
            status='Approved'
        ).exists()
        
        return JsonResponse({"has_accepted_contract": has_contract})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def check_expired_contracts(request, user_id):
    now = timezone.now()

    active_contracts_count = Contract.objects.filter(
        Q(vendor_id=user_id) | Q(seller_id=user_id),
        status='Approved',
        end_date__lte=now
    ).count()

    return JsonResponse({'expired_contracts_count': active_contracts_count})


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_not_already_existing_product_contract(request, product_id, user_id):
    try:
        # Retrieve the list of stores owned by the user
        user_stores = Store.objects.filter(owner_id=user_id).values_list('id', flat=True)
        
        # Retrieve the stores that already have an accepted contract for the given product
        stores_with_contracts = Contract.objects.filter(
            product_id=product_id,
            store_id__in=user_stores,
            status='Approved'
        ).values_list('store_id', flat=True)
        
        # Retrieve the stores that do not have an accepted contract for the given product
        stores_without_contracts = Store.objects.filter(id__in=user_stores).exclude(id__in=stores_with_contracts)
        
        # Serialize the store data
        stores_data = [{'store_id': store.id, 'store_name': store.name} for store in stores_without_contracts]
        
        # Return the serialized data in a JSON response
        return JsonResponse({"stores_without_contracts": stores_data}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
