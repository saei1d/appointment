from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from blog.views_public import blog_list_public, blog_detail_public


_original_get_app_list = admin.site.get_app_list
def _limited_staff_app_list(request, app_label=None):
    apps = _original_get_app_list(request, app_label)
    if request.user.is_superuser:
        return apps
    allowed = getattr(settings, 'ADMIN_STAFF_ALLOWED_APPS', {'blog', 'support'})
    return [app for app in apps if app['app_label'] in allowed]
admin.site.get_app_list = _limited_staff_app_list

def _staff_allowed_for_model(model_admin, request):
    allowed = getattr(settings, 'ADMIN_STAFF_ALLOWED_APPS', {'blog', 'support'})
    return request.user.is_superuser or model_admin.model._meta.app_label in allowed

for _model, _model_admin in admin.site._registry.items():
    _orig_has_view = _model_admin.has_view_permission
    _orig_has_change = _model_admin.has_change_permission
    _orig_has_add = _model_admin.has_add_permission
    _orig_has_delete = _model_admin.has_delete_permission
    def _limited_has_view(request, obj=None, _ma=_model_admin, _orig=_orig_has_view):
        return _staff_allowed_for_model(_ma, request) and _orig(request, obj)
    def _limited_has_change(request, obj=None, _ma=_model_admin, _orig=_orig_has_change):
        return _staff_allowed_for_model(_ma, request) and _orig(request, obj)
    def _limited_has_add(request, _ma=_model_admin, _orig=_orig_has_add):
        return _staff_allowed_for_model(_ma, request) and _orig(request)
    def _limited_has_delete(request, obj=None, _ma=_model_admin, _orig=_orig_has_delete):
        return _staff_allowed_for_model(_ma, request) and _orig(request, obj)
    _model_admin.has_view_permission = _limited_has_view
    _model_admin.has_change_permission = _limited_has_change
    _model_admin.has_add_permission = _limited_has_add
    _model_admin.has_delete_permission = _limited_has_delete

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('blog-admin/', include('blog.urls')),
    path('blog/', blog_list_public, name='blog_public_list'),
    path('blog/<slug:slug>/', blog_detail_public, name='blog_detail_public'),
    path('', include('provider.urls')),
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('reservations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
