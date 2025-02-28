from rest_framework import serializers
from .models import Blog


class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.fullname', read_only=True)
    
    class Meta:
        model = Blog
        fields = '__all__'