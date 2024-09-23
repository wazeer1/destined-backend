from rest_framework import serializers
from accounts.models import *
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from general.models import *
import random
import string


class CheckPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,  # Allows for international numbers
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )

    def validate_phone_number(self, value):
        # Ensure the phone number is valid and check if it already exists in the User model.
        if User.objects.filter(phone_number=value).exists():
            return value  # The phone number exists, no need to raise an error
        return value  # Phone number doesn't exist, simply return it
    

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        phone_number = data.get('phone_number')
        otp_code = data.get('otp_code')

        try:
            otp_instance = OTP.objects.get(phone_number=phone_number, otp_code=otp_code, is_active=True)

            # Check if OTP is expired
            if otp_instance.is_expired():
                raise serializers.ValidationError("OTP has expired.")
            
            # Check if maximum attempts are exceeded
            if not otp_instance.can_attempt():
                otp_instance.deactivate()
                raise serializers.ValidationError("Maximum OTP attempts exceeded.")
            
            return data
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or phone number.")

    def create_user(self, phone_number):
        """Create a new user if the phone number is not registered."""
        password = self.generate_random_password()
        user = User.objects.create_user(phone_number=phone_number, password=password)
        return user, password

    def generate_random_password(self):
        """Generate a random password."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    def get_tokens_for_user(self, user):
        """Generate access and refresh tokens for the user."""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'profile_image']
        extra_kwargs = {
            'date_of_birth': {'required': False},
            'gender': {'required': False},
            'profile_image': {'required': False},
        }

    def update(self, instance, validated_data):
        # Update the fields in the instance
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        
        instance.save()
        return instance


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['name', 'icon'] 


