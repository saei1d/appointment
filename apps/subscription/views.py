from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Plan, Subscription
from .serializer import PlanSerializer, SubscriptionSerializer
from apps.provider.models import Provider
from apps.payment.models import Transaction


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