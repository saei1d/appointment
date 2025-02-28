from rest_framework import serializers
from .models import Provider, Service, Appointment


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    provider_name = serializers.ReadOnlyField(source='provider.business_name')
    
    class Meta:
        model = Service
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='service.name')
    provider_name = serializers.ReadOnlyField(source='service.provider.business_name')
    user_name = serializers.ReadOnlyField(source='user.fullname')
    
    class Meta:
        model = Appointment
        fields = '__all__'