from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'fullname', 'city', 'user_type', 'email', 'is_active')
    search_fields = ('phone', 'fullname', 'email')
    list_filter = ('user_type', 'is_active', 'city')