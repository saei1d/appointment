from django.db import models
from django.utils import timezone
from apps.provider.models import Provider


class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    duration_days = models.PositiveIntegerField(default=30)
    can_accept_deposits = models.BooleanField(default=False)
    can_use_sms = models.BooleanField(default=False)
    can_manage_products = models.BooleanField(default=False)
    can_view_statistics = models.BooleanField(default=False)
    can_create_discounts = models.BooleanField(default=False)
    can_use_loyalty = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-end_date',)

    @property
    def is_current(self):
        today = timezone.localdate()
        return self.is_active and self.start_date <= today <= self.end_date

    def __str__(self):
        return f'{self.provider} - {self.plan}'
