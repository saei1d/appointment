from wagtail import hooks
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


@hooks.register('before_create_user')
def grant_wagtail_permissions(user):
    """Automatically grant Wagtail permissions to staff users"""
    if user.is_staff and not user.is_superuser:
        # Add the user to the "Editors" group if it exists, or create it
        editors_group, created = Group.objects.get_or_create(name='Editors')
        
        if created:
            # Give the group all necessary Wagtail permissions
            content_types = ContentType.objects.filter(
                app_label__in=['wagtailadmin', 'wagtailcore', 'wagtailimages', 'wagtaildocs']
            )
            
            permissions = Permission.objects.filter(content_type__in=content_types)
            editors_group.permissions.set(permissions)
        
        # Add user to the group
        user.groups.add(editors_group)
