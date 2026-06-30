from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('slug/check/', views.check_slug, name='check_slug'),
    path('categories/<slug:slug>/', views.category_providers, name='category_providers'),
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:service_id>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:service_id>/delete/', views.service_delete, name='service_delete'),
    path('subscription/plans/', views.subscription_plans, name='subscription_plans'),
    path('<slug:slug>/book/<int:service_id>/', views.book_service, name='book_service'),
    path('<slug:slug>/', views.provider_public_page, name='provider_public_page'),
]
