from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from reservations.models import Appointment
from reservations.services.availability import ACTIVE_STATUSES, generate_available_slots


@transaction.atomic
def create_appointment(*, customer, provider, service, date, start_time, notes=''):
    if service.provider_id != provider.id or not service.is_active:
        raise ValidationError('Invalid service for provider.')
    locked = Appointment.objects.select_for_update().filter(provider=provider, date=date, status__in=ACTIVE_STATUSES)
    list(locked)
    if start_time not in generate_available_slots(provider, service, date):
        raise ValidationError('Selected time is not available.')
    end_time = (datetime.combine(date, start_time) + timedelta(minutes=service.duration)).time()
    return Appointment.objects.create(customer=customer, provider=provider, service=service, date=date, start_time=start_time, end_time=end_time, notes=notes)
