from rest_framework import serializers
from .models import CustomUser, PhoneOTP
from django.contrib.auth.hashers import make_password

# Not directly needed, since user is created from OTP model, not through this serializer
# You can keep it if you plan to allow direct registration too
class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'email', 'phone_number', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        return CustomUser.objects.create(**validated_data)


# Used only if you want to verify OTP using phone_number (not recommended in your final version)
class PhoneOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneOTP
        fields = ['phone_number']


# For Step 1: Pre-registration and sending OTP
class PreRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return CustomUser.objects.normalize_email(value)
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        # Check if user with this data already exists
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username is already taken.")
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email is already registered.")
        if CustomUser.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError("Phone number is already in use.")

        return data
