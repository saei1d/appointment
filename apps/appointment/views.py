from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import WorkingCalendar, Appointment
from .serializer import WorkingCalendarSerializer, AppointmentSerializer
from apps.provider.models import Provider
from apps.notification.models import Notification
from apps.subscription.models import Subscription


class WorkingCalendarViewSet(viewsets.ModelViewSet):
    queryset = WorkingCalendar.objects.all()
    serializer_class = WorkingCalendarSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['provider', 'date', 'is_available']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        provider = get_object_or_404(Provider, user=self.request.user)
        serializer.save(provider=provider)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'provider', 'service', 'date', 'status']
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'provider_profile'):
            return Appointment.objects.filter(provider=user.provider_profile)
        return Appointment.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        # Check if the provider has an active subscription
        provider_id = request.data.get('provider')
        provider = get_object_or_404(Provider, id=provider_id)
        
        has_subscription = Subscription.objects.filter(
            provider=provider,
            is_active=True,
            end_date__gte=timezone.now().date()
        ).exists()
        
        if not has_subscription:
            return Response(
                {"detail": "This provider does not have an active subscription"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the time slot is available
        date = request.data.get('date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        # Check if there's a working calendar entry for this time
        calendar_available = WorkingCalendar.objects.filter(
            provider=provider,
            date=date,
            start_time__lte=start_time,
            end_time__gte=end_time,
            is_available=True
        ).exists()
        
        if not calendar_available:
            return Response(
                {"detail": "This time slot is not available"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's already an appointment for this time
        appointment_exists = Appointment.objects.filter(
            provider=provider,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['pending', 'confirmed']
        ).exists()
        
        if appointment_exists:
            return Response(
                {"detail": "This time slot is already booked"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        # Create notification for provider
        Notification.objects.create(
            user=provider.user,
            title="New Appointment",
            message=f"You have a new appointment request from {request.user.fullname}",
            notification_type="appointment"
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        
        if appointment.provider.user != request.user:
            return Response(
                {"detail": "You don't have permission to confirm this appointment"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment.status = 'confirmed'
        appointment.save()
        
        # Create notification for user
        Notification.objects.create(
            user=appointment.user,
            title="Appointment Confirmed",
            message=f"Your appointment with {appointment.provider.user.fullname} has been confirmed",
            notification_type="appointment"
        )
        
        return Response({"detail": "Appointment confirmed"})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        
        if appointment.user != request.user and appointment.provider.user != request.user:
            return Response(
                {"detail": "You don't have permission to cancel this appointment"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment.status = 'cancelled'
        appointment.save()
        
        # Create notification
        if appointment.user == request.user:
            # User cancelled
            Notification.objects.create(
                user=appointment.provider.user,
                title="Appointment Cancelled",
                message=f"Appointment with {appointment.user.fullname} has been cancelled by the client",
                notification_type="appointment"
            )
        else:
            # Provider cancelled
            Notification.objects.create(
                user=appointment.user,
                title="Appointment Cancelled",
                message=f"Your appointment with {appointment.provider.user.fullname} has been cancelled by the provider",
                notification_type="appointment"
            )
        
        return Response({"detail": "Appointment cancelled"})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        
        if appointment.provider.user != request.user:
            return Response(
                {"detail": "You don't have permission to complete this appointment"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment.status = 'completed'
        appointment.save()
        
        # Create notification for user
        Notification.objects.create(
            user=appointment.user,
            title="Appointment Completed",
            message=f"Your appointment with {appointment.provider.user.fullname} has been marked as completed",
            notification_type="appointment"
        )
        
        return Response({"detail": "Appointment completed"})