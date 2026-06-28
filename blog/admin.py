from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_published', 'published_at', 'created_at')
    list_filter = ('is_published', 'author')
    search_fields = ('title', 'content', 'author__fullname')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('انتشار', {'fields': ('title', 'slug', 'author', 'image', 'is_published', 'published_at')}),
        ('محتوا', {'fields': ('content',), 'description': 'برای تیتر، لیست، لینک و تصویر از ادیتور مرورگر/کپی از Google Docs استفاده کنید؛ HTML ساده نیز پشتیبانی می‌شود.'}),
    )

    class Media:
        js = ('https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js',)
