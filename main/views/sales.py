from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from main.models import NormalUser, Store  
from django.views.decorators.csrf import csrf_exempt
from main.models import Sale, Store
from django.db.models import Sum
from django.shortcuts import get_list_or_404
from main.models import Sale, Product, Store
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json


from main.models import Inventory, Store, Product





@csrf_exempt
def get_prices_by_id(request, id):
    results = []

    
    if id:
        try:
            product = Product.objects.get(owner=id)
            sales = Sale.objects.filter(product=product)
            for sale in sales:
                results.append({
                    'price': str(sale.price),  
                    'product_name': product.name,
                    'sale_created_date_month': sale.date.strftime('%Y-%m')  
                })
        except Product.DoesNotExist:
            pass  
        try:
            store = Store.objects.get(owner=id)
            sales = Sale.objects.filter(store=store)
            for sale in sales:
                results.append({
                    'price': str(sale.price),  
                    'store_name': store.name,
                    'sale_created_date_month': sale.date.strftime('%Y-%m')  
                })
        except Store.DoesNotExist:
            pass

        if results:
            return JsonResponse({'sales': results}, safe=False)
        else:
            return JsonResponse({'error': 'No matching sales found for the given ID'}, status=404)

    
    try:
        sales_over_time = Sale.objects.annotate(month=TruncMonth('date')).values('month').annotate(total_price=Sum('price')).order_by('month')
        
        sales_data = []
        for sale in sales_over_time:
            sales_data.append({
                'month': sale['month'].strftime('%Y-%m'),  
                'total_price': str(sale['total_price'])  
            })
            
        return JsonResponse({'sales_over_time': sales_data}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)





@csrf_exempt
def get_percentage(request, id):

    if id:
        try:
            products = Product.objects.filter(owner=id)
            stores = Store.objects.filter(owner=id)
            
            product_sales = Sale.objects.filter(product__in=products)
            store_sales = Sale.objects.filter(store__in=stores)
            
            total_sales = product_sales | store_sales
            
            # Calculate total number of sales
            total_sales_count = total_sales.count()
            
            # Calculate category counts
            categories_count = {}
            
            # Function to fetch category name from sale object
            def get_category_name(sale):
                if sale.product:
                    return sale.product.category.name if sale.product.category else 'Uncategorized'
                elif sale.store:
                    return sale.store.product_category.name if sale.store.product_category else 'Uncategorized'
                else:
                    return 'Uncategorized'
            
            # Iterate through total sales to count categories
            for sale in total_sales:
                category_name = get_category_name(sale)
                
                if category_name in categories_count:
                    categories_count[category_name] += 1
                else:
                    categories_count[category_name] = 1
            
            # Calculate percentages
            category_percentages = {}
            for category_name, count in categories_count.items():
                percentage = (count / total_sales_count) * 100
                category_percentages[category_name] = round(percentage, 2)
            
            return JsonResponse({'category_percentages': category_percentages}, safe=False)
        
        except (Product.DoesNotExist, Store.DoesNotExist):
            return JsonResponse({'error': 'Products or Stores not found for the given ID'}, status=404)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'ID parameter is required'}, status=400)







@csrf_exempt
def totalProduct(request, id):

    try:
        total_price = 0.0
        
      
        products = Product.objects.filter(owner_id=id)
        
       
        for product in products:
           
            inventory_entries_product = Inventory.objects.filter(product_id=product.id)
            
            
            for inventory in inventory_entries_product:
                total_price += float(inventory.total_quantity * inventory.available_quantity)
        
        
        stores = Store.objects.filter(owner_id=id)
        
        
        for store in stores:
            
            inventory_entries_store = Inventory.objects.filter(store_id=store.id)
            
           
            for inventory in inventory_entries_store:
                total_price += float(inventory.total_quantity * inventory.available_quantity)
        
        return JsonResponse({'total_price': total_price})
    
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Products not found for this owner'}, status=404)
    
    except Store.DoesNotExist:
        return JsonResponse({'error': 'Stores not found for this owner'}, status=404)
    
    except Inventory.DoesNotExist:
        return JsonResponse({'error': 'Inventory not found for the products and stores'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    



@csrf_exempt
def totalSales(request, id):
    if id:
        total_sales = 0
        
       
        products = Product.objects.filter(owner=id)
        for product in products:
            total_sales += Sale.objects.filter(product=product).aggregate(total_sales=Sum('price'))['total_sales'] or 0
            
        
        stores = Store.objects.filter(owner=id)
        for store in stores:
            total_sales += Sale.objects.filter(store=store).aggregate(total_sales=Sum('price'))['total_sales'] or 0

        return JsonResponse({'total_sales': str(total_sales)})
    
    return JsonResponse({'error': 'No ID provided'}, status=400)




