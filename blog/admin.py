# blog/admin.py
from django.contrib import admin
from .models import BlogPage, BlogCategory, BlogPageTag, AdPlacement, Ad


@admin.register(BlogPage)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'first_published_at', 'last_published_at']
    list_filter = ['first_published_at']
    search_fields = ['title', 'excerpt', 'body']
    readonly_fields = ['first_published_at', 'last_published_at']


@admin.register(BlogCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}






class AdInline(admin.TabularInline):
    model = Ad
    extra = 0
    fields = ['title', 'image_desktop', 'image_mobile', 'link_url', 'start_date', 'end_date', 'priority', 'is_active']
    readonly_fields = ['impression_count', 'click_count']


@admin.register(AdPlacement)
class AdPlacementAdmin(admin.ModelAdmin):
    list_display = ['name', 'placement_code', 'is_active', 'ads_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AdInline]

    def ads_count(self, obj):
        return obj.ads.count()
    ads_count.short_description = 'تعداد تبلیغات'


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'placement', 'priority', 'is_active', 'impression_count', 'click_count', 'start_date', 'end_date']
    list_filter = ['placement', 'is_active', 'start_date']
    search_fields = ['title', 'link_url']
    readonly_fields = ['impression_count', 'click_count', 'created_at']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'placement', 'link_url')
        }),
        ('تصاویر', {
            'fields': ('image_desktop', 'image_mobile')
        }),
        ('زمان‌بندی و اولویت', {
            'fields': ('start_date', 'end_date', 'priority', 'is_active')
        }),
        ('آمار', {
            'fields': ('impression_count', 'click_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
