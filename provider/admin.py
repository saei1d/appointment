from django.contrib import admin
from .models import GalleryItem, Provider, Service


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0


class GalleryInline(admin.TabularInline):
    model = GalleryItem
    extra = 0


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'is_verified', 'rating', 'total_reviews', 'created_at')
    list_filter = ('is_verified', 'typography')
    search_fields = ('user__fullname', 'user__phone', 'slug', 'address')
    inlines = [ServiceInline, GalleryInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'price', 'deposit_amount', 'duration', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'provider__user__fullname')


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'kind', 'is_active', 'created_at')
    list_filter = ('kind', 'is_active', 'category')

from .models import Product, ProductCategory

admin.site.register(ProductCategory)
admin.site.register(Product)
