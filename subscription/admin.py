from django.contrib import admin
from .models import Plan, Subscription

admin.site.register(Plan)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('provider', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'plan')
    search_fields = ('provider__user__fullname', 'provider__slug')
