from django.db import models
from apps.users.models import User


class Provider(models.Model):
    """
    Model for beauty service providers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    address = models.TextField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    profile_image = models.ImageField(upload_to='provider_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name


class Service(models.Model):
    """
    Model for services offered by providers
    """
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.provider.business_name}"


class Appointment(models.Model):
    """
    Model for appointments booked by users
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.fullname} - {self.service.name} on {self.date} at {self.start_time}"