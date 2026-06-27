from django.contrib import admin
from .models import Appointment, SpecialWorkingHour, WorkingHour

admin.site.register(WorkingHour)
admin.site.register(SpecialWorkingHour)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'provider', 'service', 'date', 'start_time', 'end_time', 'status', 'deposit_paid')
    list_filter = ('status', 'date', 'deposit_paid')
    search_fields = ('customer__fullname', 'provider__user__fullname', 'service__name')
