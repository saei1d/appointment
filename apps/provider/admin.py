from django.contrib import admin
from .models import Provider, Service, Appointment


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'is_verified', 'rating', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('business_name', 'user__fullname', 'user__phone')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'price', 'duration', 'is_active')
    list_filter = ('is_active', 'provider')
    search_fields = ('name', 'provider__business_name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__fullname', 'service__name', 'service__provider__business_name')