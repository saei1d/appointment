from django.urls import path
from . import views
urlpatterns = [
    path('', views.customer_bookings, name='customer_bookings'),
    path('past/', views.customer_bookings_past, name='customer_bookings_past'),
    path('checkout/', views.booking_checkout, name='booking_checkout'),
    path('success/<int:appointment_id>/', views.booking_success, name='booking_success'),
    path('<int:appointment_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]
