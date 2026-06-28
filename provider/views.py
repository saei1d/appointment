from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from reservations.services.availability import generate_available_slots
from reservations.services.booking import create_appointment
from provider.models import Provider, Service
from subscription.models import Plan


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


@login_required
def service_list(request):
    provider = get_object_or_404(Provider, user=request.user)
    services = provider.services.all()
    return render(request, 'providers/service_list.html', {'provider': provider, 'services': services})


@login_required
def service_create(request):
    provider = get_object_or_404(Provider, user=request.user)
    if request.method == 'POST':
        service = Service.objects.create(
            provider=provider,
            name=request.POST['name'],
            description=request.POST.get('description', ''),
            price=request.POST['price'],
            duration=request.POST['duration'],
            deposit_amount=request.POST.get('deposit_amount', 0)
        )
        messages.success(request, 'خدمت با موفقیت ایجاد شد')
        return redirect('service_list')
    return render(request, 'providers/service_form.html', {'provider': provider})


@login_required
def service_edit(request, service_id):
    provider = get_object_or_404(Provider, user=request.user)
    service = get_object_or_404(Service, id=service_id, provider=provider)
    if request.method == 'POST':
        service.name = request.POST['name']
        service.description = request.POST.get('description', '')
        service.price = request.POST['price']
        service.duration = request.POST['duration']
        service.deposit_amount = request.POST.get('deposit_amount', 0)
        service.save()
        messages.success(request, 'خدمت با موفقیت ویرایش شد')
        return redirect('service_list')
    return render(request, 'providers/service_form.html', {'provider': provider, 'service': service})


@login_required
def service_delete(request, service_id):
    provider = get_object_or_404(Provider, user=request.user)
    service = get_object_or_404(Service, id=service_id, provider=provider)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'خدمت با موفقیت حذف شد')
        return redirect('service_list')
    return render(request, 'providers/service_confirm_delete.html', {'provider': provider, 'service': service})


@login_required
def subscription_plans(request):
    provider = get_object_or_404(Provider, user=request.user)
    plans = Plan.objects.filter(is_active=True)
    return render(request, 'providers/subscription_plans.html', {'provider': provider, 'plans': plans})
