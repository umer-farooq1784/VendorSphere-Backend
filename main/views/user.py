from main import serializers
from main.models import NormalUser, Subscription
from rest_framework import generics
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid
from django.core.mail import send_mail
from django.conf import settings

# pylint: disable=no-member


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        try:
            user = NormalUser.objects.get(email=email)
        except NormalUser.DoesNotExist:
            return JsonResponse({"error": "Invalid email or password"}, status=400)

        if check_password(password, user.password):
            refresh = RefreshToken.for_user(user)

            # Include user details in the response
            user_details = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": str(user.image.url) if user.image else None,
                "phone": user.phone,
                "address": user.address,
                "city": user.city,
                "state": user.state,
                "zip": user.zip,
                "country": user.country,
                "created_at": user.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updated_at": user.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "subscription": user.subscription.name if user.subscription else None,
                "role": user.role.name if user.role else None,
            }

            return JsonResponse(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": user_details,
                },
                status=200,
            )
        else:
            return JsonResponse({"error": "Invalid email or password"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


@csrf_exempt
def signup_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        name = data.get("name")

        # Check if a NormalUser with the provided email exists
        try:
            normal_user = NormalUser.objects.get(email=email)
            return JsonResponse(
                {"error": "User with this email already exists"}, status=400
            )
        except NormalUser.DoesNotExist:
            if password != confirm_password:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            # Check if the 'Free' subscription exists, if not, create it
            try:
                with transaction.atomic():
                    free_subscription = Subscription.objects.get(name="Free")
            except Subscription.DoesNotExist:
                free_subscription = Subscription.objects.create(
                    name="Free",
                    price=0,
                    tier=1,
                    description="Free subscription",
                )

            # Hash the password before saving
            hashed_password = make_password(password)

            # Now, create the NormalUser with the hashed password and the 'Free' subscription
            normal_user = NormalUser.objects.create(
                email=email,
                password=hashed_password,
                name=name,
                subscription=free_subscription,
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(normal_user)

            return JsonResponse(
                {
                    "message": "Signup successful",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=201,
            )
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "User signed out successfully"})


@csrf_exempt
def update_profile(request):
    if request.method == "POST":
        # Assuming the data is sent as FormData
        data = request.POST  # For non-file fields
        files = request.FILES  # For file fields

        # Extract the fields from the data
        user_email = data.get("email")

        try:
            # Retrieve the user object to update
            user = NormalUser.objects.get(email=user_email)

            for key, value in data.items():
                if key == "subscription":
                    try:
                        subscription = Subscription.objects.get(name=value)
                        setattr(
                            user, key, subscription
                        )  # Assign the Subscription instance
                    except Subscription.DoesNotExist:
                        return JsonResponse(
                            {"error": f'Subscription "{value}" does not exist'},
                            status=400,
                        )
                else:
                    setattr(user, key, value)

            # Handle file fields separately
            if 'image' in files:
                user.image = files['image']

            
 

            user.save()
            user_details = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": str(user.image.url) if user.image else None,
                "phone": user.phone,
                "address": user.address,
                "city": user.city,
                "state": user.state,
                "zip": user.zip,
                "country": user.country,
                "subscription": user.subscription.name if user.subscription else None,
            }

            return JsonResponse(
                {"message": "Profile updated successfully", "user": user_details},
                status=200,
            )
        except NormalUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


@csrf_exempt
def disable_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_email = data.get("email")
        is_disabled = data.get("is_disabled")

        try:
            user = NormalUser.objects.get(email=user_email)
            user.is_disabled = is_disabled
            user.save()
            return JsonResponse(
                {"message": "User disabled status updated successfully"}, status=200
            )
        except NormalUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


# def send_forgot_password_email(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_email = data.get("email")

#         try:
#             user = NormalUser.objects.get(email=user_email)
#             token = str(uuid.uuid4())
#             subject = "Password Reset Request"
#             message = f"Click the link below to reset your password:\n\nhttp://localhost:3000/reset-password?token={token}"
#             email_from = settings.EMAIL_HOST_USER
#             recipient_list = [user.email]
#             send_mail(subject, message, email_from, recipient_list)
#             return JsonResponse(
#                 {"message": "Password reset email sent successfully"}, status=200
#             )
#         except NormalUser.DoesNotExist:
#             return JsonResponse({"error": "User not found"}, status=404)
#     else:
#         return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def delete_account(request):
    if request.method == "DELETE":
        data = json.loads(request.body)
        user_email = data.get("email")
        password = data.get("password")
        try:
            user = NormalUser.objects.get(email=user_email)
            if check_password(password, user.password):
                user.delete()
                return JsonResponse({"message": "Account deleted successfully"}, status=200)
            else:
                return JsonResponse({"error": "Invalid password"}, status=400)
        except NormalUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)


@csrf_exempt
def update_subscription(request):
    if request.method == "POST":
        try:
            # Parse the request body
            data = json.loads(request.body)
            body_data = json.loads(data['body'])

            # Extract the fields from the data
            user_email = body_data.get("email")
            subscription_name = body_data.get("subscription")
            

            # Retrieve the user object to update
            user = NormalUser.objects.get(email=user_email)

            # Retrieve the subscription object based on the received subscription name
            try:
                subscription = Subscription.objects.get(name=subscription_name)
            except Subscription.DoesNotExist:
                return JsonResponse(
                    {"error": f'Subscription "{subscription_name}" does not exist'},
                    status=400,
                )

            # Update the user's subscription
            user.subscription = subscription
            user.save()

            # Include user details in the response
            user_details = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": str(user.image.url) if user.image else None,
                "phone": user.phone,
                "address": user.address,
                "city": user.city,
                "state": user.state,
                "zip": user.zip,
                "country": user.country,
                "subscription": user.subscription.name if user.subscription else None,
                "role": user.role.name if user.role else None,
            }

            # Return the complete user details in the response
            return JsonResponse(
                {"message": "User's subscription updated successfully", "user": user_details},
                status=200,
            )
        except KeyError:
            return JsonResponse({"error": "Invalid request format"}, status=400)
        except NormalUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    
class NormalUserList(generics.ListCreateAPIView):
    queryset = NormalUser.objects.all()
    serializer_class = serializers.NormalUserSerializer
    permission_classes = [IsAuthenticated]


class NormalUserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NormalUser.objects.all()
    serializer_class = serializers.NormalUserDetailSerializer
    permission_classes = [IsAuthenticated]
