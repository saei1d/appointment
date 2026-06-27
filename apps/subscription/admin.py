from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_active', 'can_accept_deposits', 'can_manage_products', 'can_use_sms')
    list_filter = ('is_active', 'can_accept_deposits', 'can_manage_products', 'can_use_sms')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('provider', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'plan')
    search_fields = ('provider__user__fullname', 'provider__slug')
