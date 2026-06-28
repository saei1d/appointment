from datetime import datetime, timedelta
from reservations.models import Appointment

ACTIVE_STATUSES = [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]


def _ranges_for_date(provider, date):
    special = list(provider.special_working_hours.filter(date=date))
    if special:
        return [(s.start_time, s.end_time) for s in special if s.is_available]
    return [(h.start_time, h.end_time) for h in provider.working_hours.filter(weekday=date.weekday(), is_active=True)]


def generate_available_slots(provider, service, date, step_minutes=30):
    duration = timedelta(minutes=service.duration + provider.buffer_minutes)
    appointments = list(provider.appointments.filter(date=date, status__in=ACTIVE_STATUSES).only('start_time', 'end_time'))
    slots = []
    for start, end in _ranges_for_date(provider, date):
        cursor = datetime.combine(date, start)
        range_end = datetime.combine(date, end)
        while cursor + duration <= range_end:
            slot_start = cursor.time()
            slot_end = (cursor + timedelta(minutes=service.duration)).time()
            reserved_end = (cursor + duration).time()
            overlaps = any(a.start_time < reserved_end and a.reserved_end_time > slot_start for a in appointments)
            if not overlaps:
                slots.append(slot_start)
            cursor += timedelta(minutes=step_minutes)
    return slots
