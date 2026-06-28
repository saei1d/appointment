from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from reservations.services.availability import generate_available_slots
from reservations.services.booking import create_appointment
from provider.models import Provider, Service, ServiceCategory, ServiceTemplate
from subscription.models import Plan, Subscription
from blog.models import Blog


def home(request):
    q = request.GET.get('q', '').strip()
    categories = ServiceCategory.objects.filter(is_active=True).annotate(provider_count=Count('templates__provider_services__provider', distinct=True))[:8]
    providers = Provider.objects.filter(is_verified=True).select_related('user')
    if q:
        providers = providers.filter(Q(user__fullname__icontains=q) | Q(bio__icontains=q) | Q(city__icontains=q) | Q(services__name__icontains=q)).distinct()
    latest_posts = Blog.objects.filter(is_published=True).order_by('-published_at', '-created_at')[:3]
    return render(request, 'providers/home.html', {'providers': providers[:6], 'categories': categories, 'latest_posts': latest_posts, 'q': q})


def category_providers(request, slug):
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    city = request.GET.get('city') or request.user.city if request.user.is_authenticated else request.GET.get('city', '')
    if request.method == 'POST' and request.user.is_authenticated:
        city = request.POST.get('city', '').strip()
        request.user.city = city
        request.user.save(update_fields=['city', 'updated_at'])
        return redirect(f'{request.path}?city={city}')
    providers = Provider.objects.filter(is_verified=True, services__template__category=category, services__is_active=True).select_related('user').distinct()
    if city:
        providers = providers.filter(city=city)
    cities = Provider.objects.filter(is_verified=True, services__template__category=category).values_list('city', flat=True).distinct()
    return render(request, 'providers/category_providers.html', {'category': category, 'providers': providers, 'city': city, 'cities': cities})


def check_slug(request):
    slug = request.GET.get('slug', '').strip()
    available = len(slug) > 4 and not Provider.objects.filter(slug=slug).exists()
    if request.headers.get('HX-Request'):
        if available:
            return HttpResponse('<span class="text-green-600">این آدرس قابل استفاده است.</span>')
        if len(slug) <= 4:
            return HttpResponse('<span class="text-red-600">اسلاگ باید بیشتر از ۴ حرف باشد.</span>')
        return HttpResponse('<span class="text-red-600">این آدرس قبلا استفاده شده است.</span>')
    return JsonResponse({'available': available, 'valid_length': len(slug) > 4})


def provider_public_page(request, slug):
    provider = get_object_or_404(Provider.objects.select_related('user').prefetch_related('services__template__category', 'gallery_items', 'reviews'), slug=slug)
    services = provider.services.filter(is_active=True)
    return render(request, 'providers/public_page.html', {'provider': provider, 'services': services})


@login_required
def provider_dashboard(request):
    provider = get_object_or_404(Provider, user=request.user)
    appointments = provider.appointments.select_related('customer', 'service')[:10]
    subscription = provider.subscriptions.select_related('plan').filter(is_active=True).order_by('-end_date').first()
    if request.method == 'POST':
        provider.bio = request.POST.get('bio', provider.bio)
        provider.city = request.POST.get('city', provider.city)
        provider.theme_color = request.POST.get('theme_color', provider.theme_color)
        provider.background_color = request.POST.get('background_color', provider.background_color)
        provider.accent_color = request.POST.get('accent_color', provider.accent_color)
        provider.address = request.POST.get('address', provider.address)
        provider.save()
        messages.success(request, 'تنظیمات صفحه ذخیره شد.')
        return redirect('provider_dashboard')
    return render(request, 'dashboard/provider.html', {'provider': provider, 'appointments': appointments, 'subscription': subscription})


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
            messages.success(request, 'درخواست رزرو با موفقیت ثبت شد.')
            return redirect('customer_dashboard')
        except (ValidationError, ValueError) as exc:
            messages.error(request, exc.messages[0] if hasattr(exc, 'messages') else str(exc))
    return render(request, 'providers/book_service.html', {'provider': provider, 'service': service, 'selected_date': selected_date, 'slots': slots})


@login_required
def service_list(request):
    provider = get_object_or_404(Provider, user=request.user)
    services = provider.services.select_related('template__category')
    return render(request, 'providers/service_list.html', {'provider': provider, 'services': services})


@login_required
def service_create(request):
    provider = get_object_or_404(Provider, user=request.user)
    templates = ServiceTemplate.objects.filter(is_active=True).select_related('category')
    if request.method == 'POST':
        template = get_object_or_404(ServiceTemplate, id=request.POST['template'], is_active=True)
        Service.objects.create(provider=provider, template=template, name=template.name, description=request.POST.get('description', template.description), price=request.POST['price'], duration=request.POST.get('duration') or template.suggested_duration, deposit_amount=request.POST.get('deposit_amount', 0))
        messages.success(request, 'خدمت با موفقیت ایجاد شد')
        return redirect('service_list')
    return render(request, 'providers/service_form.html', {'provider': provider, 'templates': templates})


@login_required
def service_edit(request, service_id):
    provider = get_object_or_404(Provider, user=request.user)
    service = get_object_or_404(Service, id=service_id, provider=provider)
    templates = ServiceTemplate.objects.filter(is_active=True).select_related('category')
    if request.method == 'POST':
        template = get_object_or_404(ServiceTemplate, id=request.POST['template'], is_active=True)
        service.template = template; service.name = template.name
        service.description = request.POST.get('description', '')
        service.price = request.POST['price']; service.duration = request.POST['duration']
        service.deposit_amount = request.POST.get('deposit_amount', 0); service.is_active = bool(request.POST.get('is_active'))
        service.save(); messages.success(request, 'خدمت با موفقیت ویرایش شد')
        return redirect('service_list')
    return render(request, 'providers/service_form.html', {'provider': provider, 'service': service, 'templates': templates})


@login_required
def service_delete(request, service_id):
    provider = get_object_or_404(Provider, user=request.user)
    service = get_object_or_404(Service, id=service_id, provider=provider)
    if request.method == 'POST':
        service.delete(); messages.success(request, 'خدمت با موفقیت حذف شد'); return redirect('service_list')
    return render(request, 'providers/service_confirm_delete.html', {'provider': provider, 'service': service})


@login_required
def subscription_plans(request):
    provider = get_object_or_404(Provider, user=request.user)
    plans = Plan.objects.filter(is_active=True)
    if request.method == 'POST':
        plan = get_object_or_404(Plan, id=request.POST['plan_id'], is_active=True)
        Subscription.objects.create(provider=provider, plan=plan, start_date=timezone.localdate(), end_date=timezone.localdate() + timedelta(days=plan.duration_days), renewal_price_snapshot=plan.price)
        messages.success(request, 'پلن برای شما فعال شد.')
        return redirect('provider_dashboard')
    return render(request, 'providers/subscription_plans.html', {'provider': provider, 'plans': plans})
