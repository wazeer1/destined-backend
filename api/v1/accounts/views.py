import requests
import traceback

from django.db.models import Q
from django.db import transaction
from django.contrib.auth import logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout

from .serializers import *
from accounts.models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from general.functions import *
from general.models import *



@api_view(["POST"])
@permission_classes((AllowAny,))
def check_phone(request):
    try:
        serialized = CheckPhoneSerializer(data=request.data)
        if serialized.is_valid():
            phone_number = serialized.validated_data.get("phone_number")
            user_exists = User.objects.filter(phone_number=phone_number).exists()

            # if user_exists:
                # Fetch or create an OTP instance for the phone number
            otp_instance, created = OTP.objects.get_or_create(phone_number=phone_number)

            # If the OTP exists, check if it has expired
            if not created and otp_instance.is_expired():
                otp_instance.generate_otp()  # Generate a new OTP if expired
            elif not created and not otp_instance.can_attempt():
                # If not expired but 3 attempts have been made, deactivate it
                otp_instance.deactivate()
                response_data = {
                    "StatusCode": 6002,
                    "data": {
                        "message": "Too many attempts, please try again later."
                    }
                }
                return Response({"app_data": response_data}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # If OTP is valid and user can attempt, generate or resend OTP
            if created or otp_instance.is_active:
                if not created:
                    otp_instance.increment_attempts()  # Increment the number of attempts
                else:
                    otp_instance.generate_otp()  # Generate OTP if it’s a new instance

                response_data = {
                    "StatusCode": 6000,
                    "data": {
                        "message": "OTP sent successfully.",
                        "otp_code": otp_instance.otp_code,  # Send OTP code (you would send via SMS in a real app)
                        "attempts_left": 3 - otp_instance.attempts
                    }
                }
            else:
                response_data = {
                    "StatusCode": 6003,
                    "data": {
                        "message": "OTP expired, please request a new one."
                    }
                }
            # else:
            #     response_data = {
            #         "StatusCode": 6004,
            #         "data": {
            #             "message": "Phone number not registered."
            #         }
            #     }

        else:
            response_data = {
                "StatusCode": 6001,
                "data": serialized.errors,
            }
    except Exception as e:
        transaction.rollback()  # Rollback on any exception
        err_type = e.__class__.__name__
        errors = {err_type: traceback.format_exc()}
        response_data = {
            "StatusCode": 5000,
            "message": str(e),
            "errors": errors
        }
    return Response({"app_data": response_data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def verify_otp(request):
    serializer = OTPVerifySerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        
        # Check if the user already exists
        user_exists = User.objects.filter(phone_number=phone_number).exists()
        if user_exists:
            user = User.objects.get(phone_number=phone_number)
            tokens = serializer.get_tokens_for_user(user)

            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "OTP verified successfully. User logged in.",
                    "tokens": tokens,
                    "user_exist": user_exists
                }
            }
        else:
            # Create a new user and generate tokens
            user, password = serializer.create_user(phone_number)
            tokens = serializer.get_tokens_for_user(user)

            response_data = {
                "StatusCode": 6000,
                "data": {
                    "message": "OTP verified successfully. New user created.",
                    "tokens": tokens,
                    "password": password ,
                    "user_exist": user_exists
                }
            }

        # Deactivate OTP after successful verification
        otp_instance = OTP.objects.get(phone_number=phone_number)
        otp_instance.deactivate()

        return Response(response_data, status=status.HTTP_200_OK)
    
    else:
        return Response({
            "StatusCode": 6001,
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def update_user_profile(request):
    if not request.user.is_authenticated:
        return Response({
            "StatusCode": 6002,
            "message": "User is not authenticated."
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user  # Get the authenticated user
    serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "StatusCode": 6000,
            "message": "Profile updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        "StatusCode": 6001,
        "message": "Profile update failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@permission_classes((AllowAny,))  # Adjust to your permission needs
def create_interest(request):
    if request.method == 'POST':
        serializer = InterestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Interest created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        interests = Interest.objects.all()
        serializer = InterestSerializer(interests, many=True)
        return Response({"message": "Interests retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def user_interest(request):
    user = request.user 
    interest_ids = request.data.get('interest_ids')  
    
    if not interest_ids:
        return Response({"errors": "No interest IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    interests = Interests.objects.filter(id__in=interest_ids)  

    if interests.count() != len(interest_ids):
        return Response({"errors": "Some interest IDs are invalid"}, status=status.HTTP_400_BAD_REQUEST)

    
    user_interests = []
    for interest in interests:
        user_interest, created = UserInterests.objects.get_or_create(user=user, interest=interest)
        user_interests.append(user_interest)

    serializer = UserInterestSerializer(user_interests, many=True)
    
    return Response({
        "message": "User interests updated successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)