from rest_framework import serializers
from .models import (
    Provider, Service, WorkingCalendar, Appointment, Transaction,
    Wallet, Review, Notification, Ticket, TicketResponse, Blog,
    Plan, Subscription
)
from apps.users.models import User
from apps.users.serializers import RegisterSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'fullname', 'city', 'user_type', 'email']


class ProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Provider
        fields = '__all__'


class ProviderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['bio', 'address', 'profile_image']
    
    def create(self, validated_data):
        user = self.context['request'].user
        provider = Provider.objects.create(user=user, **validated_data)
        user.user_type = 'provider'
        user.save()
        return provider


class ServiceSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.user.fullname', read_only=True)
    
    class Meta:
        model = Service
        fields = '__all__'