from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *
import random

User = get_user_model()


class SendOTPView(APIView):
    throttle_classes = [AnonRateThrottle]  # محدودیت نرخ برای کاربران ناشناس

    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        # Generate OTP (default 1111 for development)
        otp = '1111'  # In production: str(random.randint(1000, 9999))

        # Store OTP in Redis with 5-minute expiration
        cache.set(phone, otp, 300)

        # SMS sending logic (comment out for actual use)
        # send_sms(phone, otp)

        return Response({'detail': 'OTP sent'})


class VerifyOTPView(APIView):
    throttle_classes = [AnonRateThrottle]  # محدودیت نرخ برای کاربران ناشناس

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        otp = serializer.validated_data['otp']

        cached_otp = cache.get(phone)

        if not cached_otp or cached_otp != otp:
            return Response(
                {'error': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete OTP from cache after verification
        cache.delete(phone)

        try:
            user = User.objects.get(phone_number=phone)
            refresh = RefreshToken.for_user(user)  # استفاده از Simple JWT
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        except User.DoesNotExist:
            return Response(
                {'detail': 'Registration required'},
                status=status.HTTP_202_ACCEPTED
            )


class RegisterView(APIView):
    throttle_classes = [AnonRateThrottle]  # محدودیت نرخ برای کاربران ناشناس

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)  # استفاده از Simple JWT

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': RegisterSerializer(user).data
        }, status=status.HTTP_201_CREATED)