from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Ticket, TicketResponse
from .serializer import TicketSerializer, TicketResponseSerializer
from apps.notification.models import Notification


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketResponseViewSet(viewsets.ModelViewSet):
    serializer_class = TicketResponseSerializer
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return TicketResponse.objects.filter(
            Q(user=self.request.user) | Q(ticket__user=self.request.user)
        ).order_by('created_at')
    
    def perform_create(self, serializer):
        ticket_id = self.request.data.get('ticket')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Update ticket status if it's the user's first response
        if ticket.user != self.request.user and ticket.status == 'open':
            ticket.status = 'in_progress'
            ticket.save()
        
        serializer.save(user=self.request.user)
        
        # Create notification for the other party
        recipient = ticket.user if ticket.user != self.request.user else None
        if recipient:
            Notification.objects.create(
                user=recipient,
                title="New Response to Your Ticket",
                message=f"You have received a new response to your ticket: {ticket.subject}",
                notification_type="system"
            )