# blog/urls.py
from django.urls import path, re_path
from . import views
from . import views_public

app_name = 'blog'

urlpatterns = [
    # ================ مسیرهای عمومی (frontend) ================
    # صفحه اصلی مجله
    path('', views_public.blog_home, name='home'),

    # دسته‌بندی‌ها
    re_path(r'^category/(?P<slug>[-\w]+)/$', views_public.category_detail, name='category'),

    # برچسب‌ها
    re_path(r'^tag/(?P<slug>[-\w]+)/$', views_public.tag_detail, name='tag'),

    # جستجو
    path('search/', views_public.blog_search, name='search'),
    path('api/instant-search/', views_public.instant_search_api, name='instant_search_api'),
    
    # نظرات
    re_path(r'^post/(?P<slug>[-\w]+)/comment/$', views_public.add_comment, name='add_comment'),
    
    # ================ مسیرهای مدیریت (admin) ================
    # مدیریت بلاگ‌ها
    path('admin-blog/list/', views.blog_list, name='admin_list'),
    path('admin-blog/create/', views.blog_create, name='admin_create'),
    path('admin-blog/<int:pk>/edit/', views.blog_edit, name='admin_edit'),
    path('admin-blog/<int:pk>/delete/', views.blog_delete, name='admin_delete'),
    
    # ================ API ها برای Editor.js ================
    path('api/auto-save/<int:pk>/', views.auto_save, name='auto_save'),
    path('api/upload-media/', views.upload_media, name='upload_media'),
    path('api/media-library/', views.media_library_api, name='media_library_api'),
    path('api/delete-media/<int:pk>/', views.delete_media, name='delete_media'),

    # صفحه داخلی مقاله (با پشتیبانی از کاراکترهای فارسی)
    re_path(r'^post/(?P<slug>[-\w]+)/$', views_public.blog_detail, name='detail'),
]