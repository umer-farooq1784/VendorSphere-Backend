import stripe
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


stripe.api_key = 'sk_test_51NXh2rAXTleCaFVGTP1KQrpGQv93uJqOjfEqQFOcq3qW0d5zCmt0P2vEXkrva1ajbpB2n5mC4fEYsdrcvAtRc8XF00RhYwhEV1'


logger = logging.getLogger(__name__)

@csrf_exempt
def create_payment_intent(request):
    try:
        request_data = json.loads(request.body.decode('utf-8'))
        body_data = json.loads(request_data["body"])
       
        payment_method_id = body_data['paymentMethodId']
        amount = body_data['amount'] * 100
        amountInCents = int(amount * 100)
        
        logger.info("Payment Method ID: %s", payment_method_id)
        
      
        intent = stripe.PaymentIntent.create(
            amount=amountInCents,  
            currency='usd',
            payment_method=payment_method_id,
            confirmation_method='manual',
            confirm=True,
            return_url='http://localhost:3000/payment'  
        )
        logger.info("PaymentIntent created successfully: %s", intent)

        return JsonResponse({'success': True, 'message': 'Payment successful'})

    except KeyError as e:
        logger.error("KeyError occurred: %s", str(e))
        return JsonResponse({'error': 'Payment Method ID not found in request body'}, status=400)

    except json.JSONDecodeError as e:
        logger.error("JSONDecodeError occurred: %s", str(e))
        return JsonResponse({'error': 'Error decoding JSON data in request body'}, status=400)

    except stripe.error.StripeError as e:
        logger.error("StripeError occurred: %s", str(e))
        return JsonResponse({'error': 'Payment failed. Please try again later.'}, status=500)

    except Exception as e:
        logger.error("Unexpected error occurred: %s", str(e))
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)
