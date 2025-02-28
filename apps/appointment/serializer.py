from rest_framework import serializers
from .models import WorkingCalendar, Appointment
from apps.users.models import User
from apps.provider.models import Provider, Service


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