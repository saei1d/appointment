from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('otp/', views.otp_auth, name='otp_auth'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('provider/register/', views.provider_register, name='provider_register'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),

]
