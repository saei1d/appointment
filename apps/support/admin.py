from django.contrib import admin
from .models import Ticket, TicketResponse


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__fullname', 'subject', 'message')


@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'created_at')
    search_fields = ('ticket__subject', 'user__fullname', 'message')