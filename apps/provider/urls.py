from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('providers/<slug:slug>/', views.provider_public_page, name='provider_public_page'),
    path('providers/<slug:slug>/book/<int:service_id>/', views.book_service, name='book_service'),
]
