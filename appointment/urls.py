from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponseRedirect
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from blog.sitemap import BlogSitemap
from provider.views import home

# ================ محدود کردن دسترسی ادمین ================
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

# ================ مسیرهای اصلی ================
sitemaps = {
    'blog': BlogSitemap,
}

def home_redirect(request):
    if getattr(settings, 'SERVER_ON', False):
        return HttpResponseRedirect('/blog/')
    else:
        return HttpResponseRedirect('/home/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
    path("cms/", include("wagtail.admin.urls")),
    path("documents/", include("wagtail.documents.urls")),
    path('', home_redirect),
    path('home/', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('reservations.urls')),
    path('review/', include('review.urls')),
    path('provider/', include('provider.urls')),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)