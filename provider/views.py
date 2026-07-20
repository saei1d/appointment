from datetime import datetime, timedelta
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from reservations.models import Appointment, WorkingHour, SpecialWorkingHour
from reservations.services.availability import generate_available_slots
from reservations.services.booking import create_appointment
from provider.models import Provider, Service, ServiceCategory, ServiceTemplate, GalleryItem
from subscription.models import Plan, Subscription
from subscription.services.features import active_subscription
from blog.models import BlogPage


def _can_accept_bookings(provider):
    return bool(active_subscription(provider) and provider.services.filter(is_active=True).exists() and provider.working_hours.filter(is_active=True).exists())


def home(request):
    q = request.GET.get('q', '').strip()
    user_city = request.user.city if request.user.is_authenticated else ''
    
    # Handle city selection
    if request.method == 'POST' and request.user.is_authenticated:
        selected_city = request.POST.get('city', '').strip()
        if selected_city:
            request.user.city = selected_city
            request.user.save(update_fields=['city', 'updated_at'])
            user_city = selected_city
        return redirect('home')
    
    # Cities are now static in the template
    
    categories = ServiceCategory.objects.filter(is_active=True).order_by('sort_order', 'name')[:8]
    templates = ServiceTemplate.objects.filter(is_active=True).select_related('category')[:8]
    popular_services = Service.objects.filter(is_active=True).annotate(booking_count=Count('appointments')).order_by('-booking_count', '-created_at')[:8]
    providers = Provider.objects.select_related('user').prefetch_related('services')
    if user_city:
        providers = providers.filter(city=user_city)
    if q:
        providers = providers.filter(Q(user__fullname__icontains=q) | Q(bio__icontains=q) | Q(city__icontains=q) | Q(services__name__icontains=q)).distinct()
    upcoming = None
    if request.user.is_authenticated:
        upcoming = request.user.appointments.select_related('provider__user', 'service').filter(date__gte=timezone.localdate(), status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]).order_by('date', 'start_time').first()
    city_services = Service.objects.filter(is_active=True, provider__city=user_city).select_related('provider', 'template__category').distinct()[:8] if user_city else []
    latest_posts = BlogPage.objects.filter(live=True).order_by('-first_published_at')[:3]
    return render(request, 'providers/home.html', {'providers': providers[:6], 'featured_providers': providers.order_by('-rating')[:5], 'categories': categories, 'templates': templates, 'popular_services': popular_services, 'city_services': city_services, 'latest_posts': latest_posts, 'q': q, 'upcoming': upcoming, 'user_city': user_city})


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
    reviews = provider.reviews.filter(is_removed=False).select_related('customer').order_by('-created_at')[:10]
    return render(request, 'providers/public_page.html', {'provider': provider, 'services': services, 'gallery': gallery, 'reviews': reviews, 'can_accept_bookings': _can_accept_bookings(provider)})


def provider_gallery(request, slug):
    provider = get_object_or_404(Provider.objects.select_related('user'), slug=slug)
    return render(request, 'providers/gallery.html', {'provider': provider, 'gallery': provider.gallery_items.filter(is_active=True)})


@login_required
def provider_dashboard(request):
    provider = get_object_or_404(Provider, user=request.user)
    appointments = provider.appointments.select_related('customer', 'service')[:10]
    subscription = provider.subscriptions.select_related('plan').filter(is_active=True).order_by('-end_date').first()
    if request.method == 'POST':
        # Handle Account city (for homepage)
        account_city = request.POST.get('account_city', '').strip()
        if account_city:
            request.user.city = account_city
            request.user.save()
        
        # Handle other fields
        for field in ['bio','theme_color','background_color','accent_color','address','contact_phone','instagram','telegram','whatsapp','google_map_url','typography','font_family']:
            if field in request.POST: setattr(provider, field, request.POST.get(field) or getattr(provider, field))
        if request.FILES.get('avatar'): provider.avatar = request.FILES['avatar']
        if request.FILES.get('cover_image'): provider.cover_image = request.FILES['cover_image']
        provider.save(); messages.success(request, 'تنظیمات صفحه ذخیره شد.'); return redirect('provider_dashboard')
    return render(request, 'dashboard/provider.html', {'provider': provider, 'appointments': appointments, 'subscription': subscription, 'weekdays': WorkingHour.Weekday.choices, 'working_hours': provider.working_hours.all()})


@login_required
def working_hours(request):
    provider = get_object_or_404(Provider, user=request.user)
    today = timezone.localdate()
    future_dates = [today + timedelta(days=i) for i in range(10)]

    def gregorian_to_jalali(gy, gm, gd):
        g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        gy2 = (gy + 1) if gm > 2 else gy
        days = 355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 + gd + g_d_m[gm - 1]
        jy = -1595 + 33 * (days // 12053)
        days %= 12053
        jy += 4 * (days // 1461)
        days %= 1461
        if days > 365:
            jy += (days - 1) // 365
            days = (days - 1) % 365
        if days < 186:
            jm = 1 + days // 31
            jd = 1 + days % 31
        else:
            jm = 7 + (days - 186) // 30
            jd = 1 + (days - 186) % 30
        return jy, jm, jd

    if request.method == 'POST':
        provider.special_working_hours.filter(date__gte=today, date__lte=future_dates[-1]).delete()
        idx = 0
        for i, dt in enumerate(future_dates):
            date_str = dt.strftime('%Y-%m-%d')
            active = request.POST.get(f'active_{date_str}')
            # همیشه اسلات‌ها ذخیره شوند، اما وضعیت is_available بر اساس active تنظیم شود
            sidx = 0
            while True:
                st = request.POST.get(f'start_{date_str}_{sidx}')
                et = request.POST.get(f'end_{date_str}_{sidx}')
                if not st or not et:
                    break
                try:
                    SpecialWorkingHour.objects.create(
                        provider=provider,
                        date=dt,
                        start_time=st,
                        end_time=et,
                        is_available=(active == 'on')
                    )
                except Exception:
                    pass
                sidx += 1
        messages.success(request, 'ساعات کاری ذخیره شد.')
        return redirect('working_hours')

    days_data = []
    for dt in future_dates:
        date_str = dt.strftime('%Y-%m-%d')
        jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
        special_hours = provider.special_working_hours.filter(date=dt)
        slots = [{'start': sh.start_time.strftime('%H:%M'), 'end': sh.end_time.strftime('%H:%M')} for sh in special_hours]
        # روز فعال است اگر حداقل یک اسلات با is_available=True داشته باشد
        has_available_slots = special_hours.filter(is_available=True).exists()
        weekday_num = (dt.weekday() + 2) % 7  # 0=شنبه, 1=یکشنبه, ... 6=جمعه
        days_data.append({
            'date': dt,
            'date_str': date_str,
            'jalali_date': f'{jy}/{jm:02d}/{jd:02d}',
            'jy': jy, 'jm': jm, 'jd': jd,
            'weekday_num': weekday_num,
            'is_active': has_available_slots,
            'slots': slots,
        })

    return render(request, 'dashboard/working_hours.html', {
        'provider': provider,
        'days_data': days_data,
        'today_jalali': gregorian_to_jalali(today.year, today.month, today.day),
    })


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
    provider = get_object_or_404(Provider, user=request.user)
    services = provider.services.select_related('template__category')
    
    # Group services by category
    categories = {}
    for service in services:
        category = service.category
        if category:
            if category not in categories:
                categories[category] = []
            categories[category].append(service)
        else:
            # Services without category
            if None not in categories:
                categories[None] = []
            categories[None].append(service)
    
    # Get selected category from query params
    selected_category_slug = request.GET.get('category', '')
    selected_category = None
    if selected_category_slug:
        try:
            selected_category = ServiceCategory.objects.get(slug=selected_category_slug)
        except ServiceCategory.DoesNotExist:
            selected_category = None
    
    return render(request, 'providers/service_list.html', {
        'provider': provider,
        'services': services,
        'grouped_services': categories,
        'selected_category': selected_category
    })

@login_required
def service_create(request):
    provider = get_object_or_404(Provider, user=request.user); templates = ServiceTemplate.objects.filter(is_active=True).select_related('category')
    # Group templates by category
    from collections import defaultdict
    grouped_templates = defaultdict(list)
    for template in templates:
        if template.category:
            grouped_templates[template.category].append(template)
        else:
            grouped_templates[None].append(template)
    if request.method == 'POST':
        template = get_object_or_404(ServiceTemplate, id=request.POST['template'], is_active=True); Service.objects.create(provider=provider, template=template, name=template.name, description=request.POST.get('description', template.description), price=request.POST['price'], duration=request.POST.get('duration') or template.suggested_duration, deposit_amount=request.POST.get('deposit_amount', 0)); messages.success(request, 'خدمت با موفقیت ایجاد شد'); return redirect('service_list')
    return render(request, 'providers/service_form.html', {'provider': provider, 'templates': templates, 'grouped_templates': dict(grouped_templates)})

@login_required
def service_edit(request, service_id):
    provider = get_object_or_404(Provider, user=request.user); service = get_object_or_404(Service, id=service_id, provider=provider); templates = ServiceTemplate.objects.filter(is_active=True).select_related('category')
    # Group templates by category
    from collections import defaultdict
    grouped_templates = defaultdict(list)
    for template in templates:
        if template.category:
            grouped_templates[template.category].append(template)
        else:
            grouped_templates[None].append(template)
    if request.method == 'POST':
        template = get_object_or_404(ServiceTemplate, id=request.POST['template'], is_active=True); service.template = template; service.name = template.name; service.description = request.POST.get('description', ''); service.price = request.POST['price']; service.duration = request.POST['duration']; service.deposit_amount = request.POST.get('deposit_amount', 0); service.is_active = bool(request.POST.get('is_active')); service.save(); messages.success(request, 'خدمت با موفقیت ویرایش شد'); return redirect('service_list')
    return render(request, 'providers/service_form.html', {'provider': provider, 'service': service, 'templates': templates, 'grouped_templates': dict(grouped_templates)})

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
