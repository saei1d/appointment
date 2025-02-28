from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'duration_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'features')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('provider__user__fullname', 'plan__name')