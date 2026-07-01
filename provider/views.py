from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from reservations.models import Appointment, WorkingHour
from reservations.services.availability import generate_available_slots
from reservations.services.booking import create_appointment
from provider.models import Provider, Service, ServiceCategory, ServiceTemplate, GalleryItem
from subscription.models import Plan, Subscription
from subscription.services.features import active_subscription
from blog.models import Blog


def _can_accept_bookings(provider):
    return bool(active_subscription(provider) and provider.services.filter(is_active=True).exists() and provider.working_hours.filter(is_active=True).exists())


def home(request):
    q = request.GET.get('q', '').strip()
    user_city = request.user.city if request.user.is_authenticated else ''
    categories = ServiceCategory.objects.filter(is_active=True).annotate(provider_count=Count('templates__provider_services__provider', distinct=True))[:8]
    providers = Provider.objects.select_related('user').prefetch_related('services')
    if user_city:
        providers = providers.filter(city=user_city)
    if q:
        providers = providers.filter(Q(user__fullname__icontains=q) | Q(bio__icontains=q) | Q(city__icontains=q) | Q(services__name__icontains=q)).distinct()
    upcoming = None
    if request.user.is_authenticated:
        upcoming = request.user.appointments.select_related('provider__user', 'service').filter(date__gte=timezone.localdate(), status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]).order_by('date', 'start_time').first()
    city_services = Service.objects.filter(is_active=True, provider__city=user_city).select_related('provider', 'template__category').distinct()[:8] if user_city else []
    latest_posts = Blog.objects.filter(is_published=True).order_by('-published_at', '-created_at')[:3]
    return render(request, 'providers/home.html', {'providers': providers[:6], 'featured_providers': providers.order_by('-rating')[:5], 'categories': categories, 'city_services': city_services, 'latest_posts': latest_posts, 'q': q, 'upcoming': upcoming, 'user_city': user_city})


def category_providers(request, slug):
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    city = request.GET.get('city', '')
    if request.method == 'POST' and request.user.is_authenticated:
        city = request.POST.get('city', '').strip(); request.user.city = city; request.user.save(update_fields=['city', 'updated_at']); return redirect(f'{request.path}?city={city}')
    if not city and request.user.is_authenticated and request.user.city: city = request.user.city
    providers = Provider.objects.filter(services__template__category=category, services__is_active=True).select_related('user').distinct()
    if city: providers = providers.filter(city=city)
    cities = Provider.objects.filter(services__template__category=category).values_list('city', flat=True).distinct()
    return render(request, 'providers/category_providers.html', {'category': category, 'providers': providers, 'city': city, 'cities': cities})


def check_slug(request):
    slug = request.GET.get('slug', '').strip()
    if any('\u0600' <= char <= '\u06FF' for char in slug):
        return HttpResponse('<span class="text-red-600">فقط حروف انگلیسی، اعداد، خط تیره و زیرخط مجاز است.</span>') if request.headers.get('HX-Request') else JsonResponse({'available': False, 'valid_length': False, 'invalid_chars': True})
    available = len(slug) > 3 and not Provider.objects.filter(slug=slug).exists()
    if request.headers.get('HX-Request'):
        return HttpResponse('<span class="text-green-600">این آدرس قابل استفاده است.</span>' if available else '<span class="text-red-600">اسلاگ کوتاه یا تکراری است.</span>')
    return JsonResponse({'available': available, 'valid_length': len(slug) > 3})


def provider_public_page(request, slug):
    provider = get_object_or_404(Provider.objects.select_related('user').prefetch_related('services__template__category', 'gallery_items', 'reviews'), slug=slug)
    services = provider.services.filter(is_active=True).select_related('template__category')
    gallery = provider.gallery_items.filter(is_active=True)[:8]
    return render(request, 'providers/public_page.html', {'provider': provider, 'services': services, 'gallery': gallery, 'can_accept_bookings': _can_accept_bookings(provider)})


def provider_gallery(request, slug):
    provider = get_object_or_404(Provider.objects.select_related('user'), slug=slug)
    return render(request, 'providers/gallery.html', {'provider': provider, 'gallery': provider.gallery_items.filter(is_active=True)})


@login_required
def provider_dashboard(request):
    provider = get_object_or_404(Provider, user=request.user)
    appointments = provider.appointments.select_related('customer', 'service')[:10]
    subscription = provider.subscriptions.select_related('plan').filter(is_active=True).order_by('-end_date').first()
    if request.method == 'POST':
        for field in ['bio','city','theme_color','background_color','accent_color','address','contact_phone','instagram','telegram','whatsapp','google_map_url','typography']:
            if field in request.POST: setattr(provider, field, request.POST.get(field) or getattr(provider, field))
        if request.FILES.get('avatar'): provider.avatar = request.FILES['avatar']
        if request.FILES.get('cover_image'): provider.cover_image = request.FILES['cover_image']
        provider.save(); messages.success(request, 'تنظیمات صفحه ذخیره شد.'); return redirect('provider_dashboard')
    return render(request, 'dashboard/provider.html', {'provider': provider, 'appointments': appointments, 'subscription': subscription, 'weekdays': WorkingHour.Weekday.choices, 'working_hours': provider.working_hours.all()})


@login_required
def working_hours(request):
    provider = get_object_or_404(Provider, user=request.user)
    if request.method == 'POST':
        provider.working_hours.all().delete()
        for day, _label in WorkingHour.Weekday.choices:
            if request.POST.get(f'active_{day}'):
                WorkingHour.objects.create(provider=provider, weekday=day, start_time=request.POST.get(f'start_{day}', '09:00'), end_time=request.POST.get(f'end_{day}', '18:00'), is_active=True)
        messages.success(request, 'ساعات کاری ذخیره شد.'); return redirect('working_hours')
    return render(request, 'dashboard/working_hours.html', {'provider': provider, 'weekdays': WorkingHour.Weekday.choices, 'working_hours': {h.weekday: h for h in provider.working_hours.all()}})


@login_required
def book_select_service(request, slug):
    provider = get_object_or_404(Provider.objects.select_related('user'), slug=slug)
    return render(request, 'providers/book_select_service.html', {'provider': provider, 'services': provider.services.filter(is_active=True)})


@login_required
def book_service(request, slug, service_id):
    provider = get_object_or_404(Provider, slug=slug); service = get_object_or_404(Service, id=service_id, provider=provider, is_active=True)
    selected_date = parse_date(request.GET.get('date', '')); slots = generate_available_slots(provider, service, selected_date) if selected_date else []
    if request.method == 'POST':
        request.session['checkout'] = {'provider_id': provider.id, 'service_id': service.id, 'date': request.POST.get('date'), 'start_time': request.POST.get('start_time'), 'notes': request.POST.get('notes', '')}
        return redirect('booking_checkout')
    return render(request, 'providers/book_service.html', {'provider': provider, 'service': service, 'selected_date': selected_date, 'slots': slots})


@login_required
def service_list(request):
    provider = get_object_or_404(Provider, user=request.user); return render(request, 'providers/service_list.html', {'provider': provider, 'services': provider.services.select_related('template__category')})

@login_required
def service_create(request):
    provider = get_object_or_404(Provider, user=request.user); templates = ServiceTemplate.objects.filter(is_active=True).select_related('category')
    if request.method == 'POST':
        template = get_object_or_404(ServiceTemplate, id=request.POST['template'], is_active=True); Service.objects.create(provider=provider, template=template, name=template.name, description=request.POST.get('description', template.description), price=request.POST['price'], duration=request.POST.get('duration') or template.suggested_duration, deposit_amount=request.POST.get('deposit_amount', 0)); messages.success(request, 'خدمت با موفقیت ایجاد شد'); return redirect('service_list')
    return render(request, 'providers/service_form.html', {'provider': provider, 'templates': templates})

@login_required
def service_edit(request, service_id):
    provider = get_object_or_404(Provider, user=request.user); service = get_object_or_404(Service, id=service_id, provider=provider); templates = ServiceTemplate.objects.filter(is_active=True).select_related('category')
    if request.method == 'POST':
        template = get_object_or_404(ServiceTemplate, id=request.POST['template'], is_active=True); service.template = template; service.name = template.name; service.description = request.POST.get('description', ''); service.price = request.POST['price']; service.duration = request.POST['duration']; service.deposit_amount = request.POST.get('deposit_amount', 0); service.is_active = bool(request.POST.get('is_active')); service.save(); messages.success(request, 'خدمت با موفقیت ویرایش شد'); return redirect('service_list')
    return render(request, 'providers/service_form.html', {'provider': provider, 'service': service, 'templates': templates})

@login_required
def service_delete(request, service_id):
    provider = get_object_or_404(Provider, user=request.user); service = get_object_or_404(Service, id=service_id, provider=provider)
    if request.method == 'POST': service.delete(); messages.success(request, 'خدمت با موفقیت حذف شد'); return redirect('service_list')
    return render(request, 'providers/service_confirm_delete.html', {'provider': provider, 'service': service})

@login_required
def subscription_plans(request):
    provider = get_object_or_404(Provider, user=request.user); plans = Plan.objects.filter(is_active=True)
    if request.method == 'POST':
        plan = get_object_or_404(Plan, id=request.POST['plan_id'], is_active=True); Subscription.objects.create(provider=provider, plan=plan, start_date=timezone.localdate(), end_date=timezone.localdate() + timedelta(days=plan.duration_days), renewal_price_snapshot=plan.price); messages.success(request, 'پلن برای شما فعال شد.'); return redirect('provider_dashboard')
    return render(request, 'providers/subscription_plans.html', {'provider': provider, 'plans': plans})


def onboarding_welcome(request): return render(request, 'onboarding/welcome.html')

def onboarding_category(request):
    if request.method == 'POST': request.session['onboarding'] = {'category_slug': request.POST.get('category_slug')}; return redirect('onboarding_type' if request.user.is_authenticated else f"{reverse('otp_auth')}?next={reverse('onboarding_type')}")
    return render(request, 'onboarding/choose_service.html', {'categories': ServiceCategory.objects.filter(is_active=True)})

@login_required
def onboarding_type(request):
    state = request.session.get('onboarding', {}); category = get_object_or_404(ServiceCategory, slug=state.get('category_slug'), is_active=True)
    templates = ServiceTemplate.objects.filter(category=category, is_active=True, provider_services__is_active=True, provider_services__provider__city=request.user.city).distinct()
    if request.method == 'POST': state['template_id'] = request.POST.get('template_id'); request.session['onboarding'] = state; return redirect('onboarding_providers')
    return render(request, 'onboarding/choose_type.html', {'category': category, 'templates': templates})

@login_required
def onboarding_providers(request):
    state = request.session.get('onboarding', {}); template = get_object_or_404(ServiceTemplate, id=state.get('template_id'), is_active=True)
    providers = Provider.objects.filter(city=request.user.city, services__template=template, services__is_active=True).select_related('user').distinct()
    return render(request, 'onboarding/choose_providers.html', {'template': template, 'providers': providers})
