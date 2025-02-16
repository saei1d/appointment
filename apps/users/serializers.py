from rest_framework import serializers
from .models import User
import re


class PhoneSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError("Phone number must be entered in the format: 09XXXXXXXXXXXXX")
        return value


class VerifyOTPSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    otp = serializers.CharField(min_length=4, max_length=4)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'fullname']
