from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import Group
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-created_at',)
    list_display = ('phone', 'fullname', 'role', 'city', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('phone', 'fullname', 'email')
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Profile', {'fields': ('fullname', 'email', 'city', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'fullname', 'role', 'is_staff', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # First save the user to get an ID
        super().save_model(request, obj, form, change)
        
        # When creating a new user with is_staff=True, automatically add to Editors group
        if not change and obj.is_staff:
            try:
                editors_group = Group.objects.get(name='Editors')
                obj.groups.add(editors_group)
            except Group.DoesNotExist:
                # Create the Editors group if it doesn't exist
                editors_group = Group.objects.create(name='Editors')
                obj.groups.add(editors_group)
