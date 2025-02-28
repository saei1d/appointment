from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import models

from .models import Review
from .serializer import ReviewSerializer
from apps.appointment.models import Appointment
from apps.notification.models import Notification


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'provider', 'appointment']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def create(self, request, *args, **kwargs):
        appointment_id = request.data.get('appointment')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check if the user is the one who had the appointment
        if appointment.user != request.user:
            return Response(
                {"detail": "You can only review appointments you've attended"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if the appointment is completed
        if appointment.status != 'completed':
            return Response(
                {"detail": "You can only review completed appointments"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if a review already exists
        if Review.objects.filter(appointment=appointment).exists():
            return Response(
                {"detail": "You have already reviewed this appointment"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(
            user=request.user,
            provider=appointment.provider
        )
        
        # Update provider rating
        provider = appointment.provider
        reviews = Review.objects.filter(provider=provider)
        provider.total_reviews = reviews.count()
        provider.rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
        provider.save()
        
        # Create notification for provider
        Notification.objects.create(
            user=provider.user,
            title="New Review",
            message=f"You have received a new review from {request.user.fullname}",
            notification_type="system"
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)