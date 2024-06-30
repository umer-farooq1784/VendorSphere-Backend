from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # Import AllowAny permission
from main.models import ProductCategory

#pylint: disable=no-member

@api_view(['GET'])
@permission_classes([AllowAny])  # Exclude authentication
def category_names(request):
    if request.method == 'GET':
        categories = ProductCategory.objects.all()
        list_of_category_names = [category.name for category in categories]
        return Response(list_of_category_names)
