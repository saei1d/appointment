from rest_framework import serializers
from .models import Ticket, TicketResponse


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