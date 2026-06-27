from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from apps.appointment.services.availability import generate_available_slots
from apps.appointment.services.booking import create_appointment
from apps.provider.models import Provider, Service


def home(request):
    providers = Provider.objects.filter(is_verified=True).select_related('user')[:24]
    return render(request, 'providers/home.html', {'providers': providers})


def provider_public_page(request, slug):
    provider = get_object_or_404(Provider.objects.select_related('user').prefetch_related('services', 'gallery_items', 'reviews'), slug=slug)
    services = provider.services.filter(is_active=True)
    return render(request, 'providers/public_page.html', {'provider': provider, 'services': services})


@login_required
def provider_dashboard(request):
    provider = get_object_or_404(Provider, user=request.user)
    appointments = provider.appointments.select_related('customer', 'service')[:10]
    return render(request, 'dashboard/provider.html', {'provider': provider, 'appointments': appointments})


@login_required
def book_service(request, slug, service_id):
    provider = get_object_or_404(Provider, slug=slug)
    service = get_object_or_404(Service, id=service_id, provider=provider, is_active=True)
    selected_date = parse_date(request.GET.get('date', ''))
    slots = generate_available_slots(provider, service, selected_date) if selected_date else []
    if request.method == 'POST':
        selected_date = parse_date(request.POST.get('date', ''))
        start_time = datetime.strptime(request.POST['start_time'], '%H:%M:%S').time()
        try:
            create_appointment(customer=request.user, provider=provider, service=service, date=selected_date, start_time=start_time, notes=request.POST.get('notes', ''))
            messages.success(request, 'Appointment requested successfully.')
            return redirect('provider_public_page', slug=slug)
        except (ValidationError, ValueError) as exc:
            messages.error(request, exc.messages[0] if hasattr(exc, 'messages') else str(exc))
    return render(request, 'providers/book_service.html', {'provider': provider, 'service': service, 'selected_date': selected_date, 'slots': slots})
