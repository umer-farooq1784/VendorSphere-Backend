from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os, json
from rest_framework import status


@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject = data.get('subject')
            message = data.get('message')
            receiver_email = os.environ.get('EMAIL_USER')  
            sender_email = data.get('sender_email')


            if sender_email is None or sender_email.strip() == "":
                return JsonResponse({"error": "provide a valid mail"}, status=status.HTTP_404_NOT_FOUND)
            send_mail(
                subject,
                message,
                sender_email,
                [receiver_email],
                fail_silently=False,
                html_message=message,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)},status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'},status=status.HTTP_404_NOT_FOUND)
