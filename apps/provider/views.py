from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Provider, Service
from .serializer import ProviderSerializer, ProviderCreateSerializer, ServiceSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user__city']
    search_fields = ['user__fullname', 'bio', 'address']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProviderCreateSerializer
        return ProviderSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        provider = serializer.save()
        return Response(ProviderSerializer(provider).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        provider = self.get_object()
        services = Service.objects.filter(provider=provider)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['provider', 'is_active']
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        provider = get_object_or_404(Provider, user=self.request.user)
        serializer.save(provider=provider)