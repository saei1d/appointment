import random
from datetime import timedelta
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import User, OTP
from provider.models import Provider


def otp_auth(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = request.POST.get('code')
        
        # Step 1: Send OTP
        if not code:
            if not phone:
                return render(request, 'accounts/otp.html', {'error': 'Phone number is required'})
            
            # Generate 5-digit OTP
            otp_code = str(random.randint(10000, 99999))
            expires_at = timezone.now() + timedelta(minutes=5)
            
            # Save OTP
            OTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
            OTP.objects.create(phone=phone, code=otp_code, expires_at=expires_at)
            
            # Print OTP for testing (in production, send via SMS)
            print(f'OTP for {phone}: {otp_code}')
            
            return render(request, 'accounts/otp.html', {'phone': phone, 'otp_sent': True})
        
        # Step 2: Verify OTP
        else:
            otp = OTP.objects.filter(phone=phone, code=code, is_used=False).first()
            
            if not otp or not otp.is_valid():
                return render(request, 'accounts/otp.html', {'phone': phone, 'error': 'Invalid or expired code'})
            
            # Mark OTP as used
            otp.is_used = True
            otp.save()
            
            # Get or create user
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={'role': User.Role.CUSTOMER}
            )
            
            # Login user
            login(request, user)
            
            return redirect('home')
    
    return render(request, 'accounts/otp.html')


@login_required
def provider_register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        slug = request.POST.get('slug')
        bio = request.POST.get('bio', '')
        contact_phone = request.POST.get('contact_phone', '')
        instagram = request.POST.get('instagram', '')
        telegram = request.POST.get('telegram', '')
        whatsapp = request.POST.get('whatsapp', '')
        address = request.POST.get('address', '')
        
        city = request.POST.get('city', '')
        if len(slug or '') <= 4 or Provider.objects.filter(slug=slug).exclude(user=request.user).exists():
            messages.error(request, 'اسلاگ باید بیشتر از ۴ حرف و یکتا باشد.')
            return render(request, 'accounts/provider_register.html')
        request.user.fullname = fullname
        request.user.role = User.Role.PROVIDER
        request.user.city = city
        request.user.save()
        provider, _ = Provider.objects.update_or_create(
            user=request.user,
            defaults={'slug': slug, 'city': city, 'bio': bio, 'contact_phone': contact_phone, 'instagram': instagram, 'telegram': telegram, 'whatsapp': whatsapp, 'address': address}
        )
        messages.success(request, 'ثبت اولیه ذخیره شد؛ حالا یک پلن انتخاب کنید.')
        return redirect('subscription_plans')
    
    return render(request, 'accounts/provider_register.html')


@login_required
def customer_dashboard(request):
    appointments = request.user.appointments.select_related('provider__user', 'service').order_by('-date', '-start_time')[:10]
    return render(request, 'accounts/customer_dashboard.html', {'appointments': appointments})
