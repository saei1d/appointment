from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.provider.models import Provider, Service


class WorkingHour(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Monday'; TUESDAY = 1, 'Tuesday'; WEDNESDAY = 2, 'Wednesday'; THURSDAY = 3, 'Thursday'; FRIDAY = 4, 'Friday'; SATURDAY = 5, 'Saturday'; SUNDAY = 6, 'Sunday'
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='working_hours')
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('weekday', 'start_time')
        unique_together = ('provider', 'weekday', 'start_time', 'end_time')

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('Start time must be before end time.')


class SpecialWorkingHour(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='special_working_hours')
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ('date', 'start_time')

    def clean(self):
        if self.is_available and (not self.start_time or not self.end_time):
            raise ValidationError('Available special days need start and end times.')
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Start time must be before end time.')


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    deposit_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date', 'start_time')
        indexes = [models.Index(fields=['provider', 'date', 'start_time', 'end_time', 'status'])]

    @property
    def reserved_end_time(self):
        dt = datetime.combine(self.date, self.end_time) + timedelta(minutes=self.provider.buffer_minutes)
        return dt.time()

    def __str__(self):
        return f'{self.customer} - {self.service} on {self.date} {self.start_time}'
