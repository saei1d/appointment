from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProviderViewSet, ServiceViewSet, AppointmentViewSet

router = DefaultRouter()
router.register(r'providers', ProviderViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]