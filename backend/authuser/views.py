import random
from django.core.mail import send_mail
from .models import PhoneOTP, CustomUser
from .serializers import PreRegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError

def send_otp(email):
    otp = str(random.randint(100000, 999999))
    subject = 'SafarSathi - Your One-Time Password (OTP)'
    message = f'''
Dear User,

Thank you for choosing SafarSathi!

Your One-Time Password (OTP) for registration is: {otp}

Please enter this code to verify your email address. This OTP is valid for a short period only.

If you did not initiate this request, please ignore this email.

Regards,
SafarSathi Team
    '''
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    print(f"[DEBUG] OTP sent to email {email}: {otp}")
    return otp

class PreRegisterUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = PreRegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            normalized_email = CustomUser.objects.normalize_email(data['email'])

            # Check if user exists using normalized email
            if CustomUser.objects.filter(email=normalized_email).exists() or \
               CustomUser.objects.filter(phone_number=data['phone_number']).exists() or \
               CustomUser.objects.filter(username=data['username']).exists():
                return Response({'error': 'User with these details already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a temporary CustomUser object without saving to DB
            user = CustomUser(
                username=data['username'],
                email=normalized_email,
                phone_number=data['phone_number'],
                name=data['name']
            )
            user.set_password(data['password'])  # Hash the password

            # Remove previous OTP entries for this user
            PhoneOTP.objects.filter(user__email=normalized_email).delete()

            otp = send_otp(normalized_email)

            # Save the user temporarily and create PhoneOTP
            user.save()
            PhoneOTP.objects.create(
                user=user,
                otp=otp,
                is_verified=False
            )

            return Response({'message': 'OTP has been sent to your email address.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyAndRegisterUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = CustomUser.objects.normalize_email(request.data.get('email'))
        otp = request.data.get('otp')

        try:
            record = PhoneOTP.objects.get(user__email=email)

            if record.otp != otp:
                return Response({'error': 'Invalid OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

            if record.is_verified:
                return Response({'error': 'This OTP has already been used to register a user.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if record.is_expired():
                record.delete()
                record.user.delete()  # Delete the temporary user
                return Response({'error': 'OTP has expired. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark OTP as verified
            record.is_verified = True
            record.save()

            # User is already created, no need to create again
            return Response({'message': 'Your account has been successfully created and verified.'}, status=status.HTTP_200_OK)

        except PhoneOTP.DoesNotExist:
            return Response({'error': 'No OTP record found for this email. Please register again.'}, status=status.HTTP_404_NOT_FOUND)

# Remaining views (LoginUser, LogoutView, CurrentUserView, PasswordResetRequestView, PasswordResetConfirmView) remain unchanged
class LoginUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username_or_email = request.data.get('username')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({'error': 'Username/Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if '@' in username_or_email:
            try:
                user = CustomUser.objects.get(email=username_or_email)
            except CustomUser.DoesNotExist:
                pass
        else:
            user = authenticate(username=username_or_email, password=password)

        if not user and '@' in username_or_email:
            try:
                user = CustomUser.objects.get(email=username_or_email)
                if not user.check_password(password):
                    user = None
            except CustomUser.DoesNotExist:
                user = None

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful.',
                'token': token.key,
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'name': user.name,
                    'phone_number': user.phone_number,
                }
            })
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logout successful. Your session has been securely ended.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong during logout.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number
        }, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        send_mail(
            'Password Reset Request',
            f'Click the link below to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )
        return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"error": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')
            if new_password != confirm_password:
                return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)