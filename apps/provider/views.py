from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models import (
    Provider, Service, WorkingCalendar, Appointment, Transaction,
    Wallet, Review, Notification, Ticket, TicketResponse, Blog,
    Plan, Subscription
)
from .serializer import (
    ProviderSerializer, ProviderCreateSerializer, ServiceSerializer, 
    WorkingCalendarSerializer, AppointmentSerializer, TransactionSerializer,
    WalletSerializer, ReviewSerializer, NotificationSerializer, TicketSerializer,
    TicketResponseSerializer, BlogSerializer, PlanSerializer, SubscriptionSerializer
)


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
    
    @action(detail=True, methods=['get'])
    def calendar(self, request, pk=None):
        provider = self.get_object()
        # Get calendar for next 10 days
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=10)
        calendar = WorkingCalendar.objects.filter(
            provider=provider,
            date__gte=start_date,
            date__lte=end_date,
            is_available=True
        )
        serializer = WorkingCalendarSerializer(calendar, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        provider = self.get_object()
        appointments = Appointment.objects.filter(provider=provider)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        provider = self.get_object()
        reviews = Review.objects.filter(provider=provider)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subscription(self, request, pk=None):
        provider = self.get_object()
        try:
            subscription = Subscription.objects.filter(
                provider=provider,
                is_active=True,
                end_date__gte=timezone.now().date()
            ).latest('end_date')
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response({"detail": "No active subscription found"}, status=status.HTTP_404_NOT_FOUND)


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


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'transaction_type', 'status']
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)


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


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"detail": "Notification marked as read"})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(user=request.user).update(is_read=True)
        return Response({"detail": "All notifications marked as read"})


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


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'provider_profile'):
            return Subscription.objects.filter(provider=user.provider_profile)
        return Subscription.objects.none()
    
    def create(self, request, *args, **kwargs):
        plan_id = request.data.get('plan')
        plan = get_object_or_404(Plan, id=plan_id)
        
        # Check if user is a provider
        try:
            provider = Provider.objects.get(user=request.user)
        except Provider.DoesNotExist:
            return Response(
                {"detail": "You need to be a provider to subscribe to a plan"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculate subscription dates
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=plan.duration_days)
        
        # Create subscription
        serializer = self.get_serializer(data={
            'provider': provider.id,
            'plan': plan.id,
            'start_date': start_date,
            'end_date': end_date,
            'is_active': True
        })
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            amount=plan.price,
            transaction_type='payment',
            status='completed',
            reference_id=f"sub_{subscription.id}"
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)