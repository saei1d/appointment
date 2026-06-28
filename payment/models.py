from django.conf import settings
from django.db import models
from provider.models import Provider


class Wallet(models.Model):
    provider = models.OneToOneField(Provider, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    pending = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    withdrawn = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Wallet: {self.provider}'


class WalletTransaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = 'deposit', 'Deposit'
        WITHDRAWAL = 'withdrawal', 'Withdrawal'
        ADJUSTMENT = 'adjustment', 'Adjustment'
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=14, decimal_places=0)
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WithdrawalRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=14, decimal_places=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
