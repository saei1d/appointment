from django.contrib import admin
from .models import WorkingCalendar, Appointment


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