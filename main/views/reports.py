from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from main.models import Report, NormalUser, Store, Product
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

#pylint: disable=no-member

@csrf_exempt
@permission_classes([AllowAny])
def report_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reported_by_id = data.get('reported_by')
            reported_id = data.get('reported_id')
            report_type = data.get('report_type')
            content = data.get('content')

            if(report_type == 'Store'):
                reported_user_id = Store.objects.get(pk=reported_id).owner.id

            elif(report_type == 'Product'):
                reported_user_id = Product.objects.get(pk=reported_id).owner.id

            if not reported_by_id or not reported_user_id or not reason:
                return JsonResponse({'error': 'Missing required fields: reported_by, reported_user, and reason'}, status=400)

            reported_by = get_object_or_404(NormalUser, id=reported_by_id)
            reported_user = get_object_or_404(NormalUser, id=reported_user_id)

            report = Report(
                reported_by=reported_by,
                reported_user=reported_user,
                details=content,
            )
            report.clean()  # Validates the model (e.g., checks if details are provided for 'Other' reason)
            report.save()

            return JsonResponse({'message': 'User reported successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValidationError as ve:
            return JsonResponse({'error': ve.message}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method. Only POST is allowed.'}, status=405)
