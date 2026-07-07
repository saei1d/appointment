"""SSR project: views for this app are added incrementally as templates are built."""
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from provider.models import Provider
from .models import Review


def add_review(request, slug):
    provider = get_object_or_404(Provider, slug=slug)
    
    if not request.user.is_authenticated:
        messages.error(request, 'برای ثبت نظر باید وارد شوید')
        return redirect('otp_auth')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            # بررسی اینکه کاربر قبلاً نظر داده است
            if Review.objects.filter(provider=provider, customer=request.user).exists():
                messages.error(request, 'شما قبلاً برای این ارائه‌دهنده نظر ثبت کرده‌اید')
            else:
                Review.objects.create(
                    provider=provider,
                    customer=request.user,
                    rating=int(rating),
                    comment=comment
                )
                messages.success(request, 'نظر شما با موفقیت ثبت شد')
    
    return redirect('provider_public_page', slug=slug)
