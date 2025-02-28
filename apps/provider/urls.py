from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProviderViewSet, ServiceViewSet, WorkingCalendarViewSet, AppointmentViewSet,
    TransactionViewSet, WalletViewSet, ReviewViewSet, NotificationViewSet,
    TicketViewSet, TicketResponseViewSet, BlogViewSet, PlanViewSet, SubscriptionViewSet
)

router = DefaultRouter()
router.register(r'providers', ProviderViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'calendar', WorkingCalendarViewSet)
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'wallet', WalletViewSet, basename='wallet')
router.register(r'reviews', ReviewViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'ticket-responses', TicketResponseViewSet, basename='ticket-response')
router.register(r'blogs', BlogViewSet)
router.register(r'plans', PlanViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]