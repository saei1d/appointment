from django.contrib import admin
from .models import (
    Provider, Service, WorkingCalendar, Appointment, Transaction,
    Wallet, Review, Notification, Ticket, TicketResponse, Blog,
    Plan, Subscription
)

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_verified', 'rating', 'total_reviews', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('user__fullname', 'user__phone', 'bio', 'address')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'provider', 'price', 'duration', 'deposit_amount', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'provider__user__fullname')

@admin.register(WorkingCalendar)
class WorkingCalendarAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'is_available')
    search_fields = ('provider__user__fullname',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'provider', 'service', 'date', 'start_time', 'end_time', 'status', 'deposit_paid')
    list_filter = ('status', 'deposit_paid', 'date')
    search_fields = ('user__fullname', 'provider__user__fullname', 'service__name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status')
    search_fields = ('user__fullname', 'reference_id')

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance', 'updated_at')
    search_fields = ('user__fullname',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'provider', 'appointment', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__fullname', 'provider__user__fullname', 'comment')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__fullname', 'title', 'message')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__fullname', 'subject', 'message')

@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'created_at')
    search_fields = ('ticket__subject', 'user__fullname', 'message')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_published', 'published_at', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'content', 'author__fullname')
    prepopulated_fields = {'slug': ('title',)}

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