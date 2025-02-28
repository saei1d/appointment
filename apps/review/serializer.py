from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.fullname', read_only=True)
    provider_name = serializers.CharField(source='provider.user.fullname', read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'