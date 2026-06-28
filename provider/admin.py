from django.contrib import admin
from .models import GalleryItem, Provider, Service, ServiceCategory, ServiceTemplate, Product, ProductCategory


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    fields = ('template', 'name', 'price', 'duration', 'deposit_amount', 'is_active')


class GalleryInline(admin.TabularInline):
    model = GalleryItem
    extra = 0


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ServiceTemplate)
class ServiceTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'suggested_duration', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'city', 'is_verified', 'rating', 'created_at')
    list_filter = ('is_verified', 'city', 'typography')
    search_fields = ('user__fullname', 'user__phone', 'slug', 'address', 'city')
    inlines = [ServiceInline, GalleryInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'template', 'price', 'duration', 'is_active')
    list_filter = ('is_active', 'template__category')
    search_fields = ('name', 'provider__user__fullname')


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'kind', 'is_active', 'created_at')
    list_filter = ('kind', 'is_active', 'category')

admin.site.register(ProductCategory)
admin.site.register(Product)
