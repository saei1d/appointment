from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Blog
from .serializer import BlogSerializer


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.filter(is_published=True)
    serializer_class = BlogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'content']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)