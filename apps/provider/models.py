from django.db import models
from apps.users.models import User


class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='provider_profiles/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.fullname} - {self.user.phone}"


class Service(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.provider.user.fullname}"