from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class Provider(models.Model):
    class Typography(models.TextChoices):
        SANS = 'sans', 'Sans'
        SERIF = 'serif', 'Serif'
        ROUNDED = 'rounded', 'Rounded'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_profile')
    slug = models.SlugField(max_length=80, unique=True, help_text='Public booking URL slug')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='providers/avatars/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='providers/covers/', blank=True, null=True)
    theme_color = models.CharField(max_length=20, default='#ec4899')
    background_color = models.CharField(max_length=20, default='#fff7fb')
    accent_color = models.CharField(max_length=20, default='#111827')
    typography = models.CharField(max_length=20, choices=Typography.choices, default=Typography.SANS)
    contact_phone = models.CharField(max_length=20, blank=True)
    instagram = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    google_map_url = models.URLField(blank=True)
    buffer_minutes = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.fullname or self.user.phone)[:70]
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.fullname} ({self.slug})'


class Service(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    duration = models.PositiveIntegerField(help_text='Duration in minutes')
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.deposit_amount and self.price and self.deposit_amount > self.price:
            raise ValidationError({'deposit_amount': 'Deposit cannot exceed service price.'})

    def __str__(self):
        return self.name


class GalleryItem(models.Model):
    class Kind(models.TextChoices):
        IMAGE = 'image', 'Image'
        BEFORE_AFTER = 'before_after', 'Before / After'

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='gallery_items')
    title = models.CharField(max_length=120, blank=True)
    category = models.CharField(max_length=80, blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.IMAGE)
    image = models.ImageField(upload_to='gallery/')
    before_image = models.ImageField(upload_to='gallery/before_after/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductCategory(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='product_categories')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('provider', 'name')

    def __str__(self):
        return self.name


class Product(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    discount_starts_at = models.DateTimeField(null=True, blank=True)
    discount_ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
