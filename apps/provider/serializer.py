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


class WorkingCalendarSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.user.fullname', read_only=True)
    
    class Meta:
        model = WorkingCalendar
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    provider_name = serializers.CharField(source='provider.user.fullname', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    
    class Meta:
        model = Wallet
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    provider_name = serializers.CharField(source='provider.user.fullname', read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'


class TicketResponseSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    
    class Meta:
        model = TicketResponse
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.fullname', read_only=True)
    
    class Meta:
        model = Blog
        fields = '__all__'


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.user.fullname', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    
    class Meta:
        model = Subscription
        fields = '__all__'