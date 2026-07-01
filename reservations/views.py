from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from provider.models import Provider, Service
from reservations.models import Appointment
from reservations.services.booking import create_appointment

@login_required
def booking_checkout(request):
    data = request.session.get('checkout')
    if not data:
        messages.error(request, 'زمان رزرو انتخاب نشده است.'); return redirect('home')
    provider = get_object_or_404(Provider.objects.select_related('user'), id=data['provider_id'])
    service = get_object_or_404(Service, id=data['service_id'], provider=provider)
    date = parse_date(data['date']); start_time = datetime.strptime(data['start_time'], '%H:%M:%S').time()
    if request.method == 'POST':
        try:
            appointment = create_appointment(customer=request.user, provider=provider, service=service, date=date, start_time=start_time, notes=data.get('notes', ''))
            request.session.pop('checkout', None)
            return redirect('booking_success', appointment_id=appointment.id)
        except (ValidationError, ValueError) as exc:
            messages.error(request, exc.messages[0] if hasattr(exc, 'messages') else str(exc))
    return render(request, 'bookings/checkout.html', {'provider': provider, 'service': service, 'date': date, 'start_time': start_time, 'notes': data.get('notes', '')})

@login_required
def booking_success(request, appointment_id):
    appointment = get_object_or_404(request.user.appointments.select_related('provider__user', 'service'), id=appointment_id)
    return render(request, 'bookings/success.html', {'appointment': appointment})

@login_required
def customer_bookings(request):
    today = timezone.localdate()
    appointments = request.user.appointments.select_related('provider__user', 'service').filter(date__gte=today, status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]).order_by('date', 'start_time')
    return render(request, 'bookings/list.html', {'appointments': appointments, 'mode': 'upcoming'})

@login_required
def customer_bookings_past(request):
    today = timezone.localdate()
    appointments = request.user.appointments.select_related('provider__user', 'service').filter(date__lt=today).order_by('-date', '-start_time')
    return render(request, 'bookings/list.html', {'appointments': appointments, 'mode': 'past'})

@login_required
def cancel_booking(request, appointment_id):
    appointment = get_object_or_404(request.user.appointments, id=appointment_id)
    if request.method == 'POST' and appointment.date >= timezone.localdate() and appointment.status in [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]:
        appointment.status = Appointment.Status.CANCELLED; appointment.save(update_fields=['status', 'updated_at']); messages.success(request, 'رزرو لغو شد.')
    return redirect('customer_bookings')
