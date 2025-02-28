from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Provider, Service, Appointment
from .serializer import ProviderSerializer, ServiceSerializer, AppointmentSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Provider model
    """
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['business_name', 'description', 'address']
    filterset_fields = ['is_verified']

    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        """
        Get all services offered by a provider
        """
        provider = self.get_object()
        services = Service.objects.filter(provider=provider)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Service model
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['provider', 'is_active']


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Appointment model
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'service', 'date', 'status']

    def get_queryset(self):
        """
        Filter appointments based on user type
        """
        user = self.request.user
        if user.is_authenticated:
            if user.user_type == 'provider':
                # Provider sees appointments for their services
                try:
                    provider = Provider.objects.get(user=user)
                    return Appointment.objects.filter(service__provider=provider)
                except Provider.DoesNotExist:
                    return Appointment.objects.none()
            else:
                # Regular user sees their own appointments
                return Appointment.objects.filter(user=user)
        return Appointment.objects.none()

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        Get available appointment slots for a service on a specific date
        """
        service_id = request.query_params.get('service_id')
        date = request.query_params.get('date')
        
        if not service_id or not date:
            return Response({"error": "service_id and date parameters are required"}, status=400)
        
        try:
            service = Service.objects.get(id=service_id)
            # Logic to find available slots based on service duration and existing appointments
            # This is a simplified example
            booked_appointments = Appointment.objects.filter(
                service=service,
                date=date,
                status__in=['pending', 'confirmed']
            )
            
            # Calculate available slots based on booked appointments
            # This would need more complex logic in a real application
            
            return Response({"available_slots": ["09:00", "10:00", "11:00"]})
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=404)