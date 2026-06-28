from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('', views.otp_auth, name='otp_auth'),
    path('provider/register/', views.provider_register, name='provider_register'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
]
