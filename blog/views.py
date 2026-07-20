# blog/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator
import json
from .models import BlogPage, BlogCategory, BlogPageTag
from taggit.models import Tag
from .forms import BlogForm


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_list(request):
    """لیست همه بلاگ‌ها با فیلترهای متنوع"""
    posts = BlogPage.objects.all().select_related('owner', 'main_image').prefetch_related('categories', 'tags')
    
    # فیلتر بر اساس وضعیت
    status = request.GET.get('status')
    if status == 'live':
        posts = posts.filter(live=True)
    elif status == 'draft':
        posts = posts.filter(live=False)
    
    # فیلتر بر اساس دسته‌بندی
    category = request.GET.get('category')
    if category:
        posts = posts.filter(categories__slug=category)
    
    # فیلتر بر اساس برچسب
    tag = request.GET.get('tag')
    if tag:
        posts = posts.filter(tags__slug=tag)
    
    # جستجو
    search = request.GET.get('search')
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(excerpt__icontains=search) |
            Q(body__icontains=search)
        )
    
    # مرتب‌سازی
    sort = request.GET.get('sort', '-first_published_at')
    if sort in ['first_published_at', '-first_published_at', 'title', '-title']:
        posts = posts.order_by(sort)
    
    # Pagination
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # دریافت لیست دسته‌بندی‌ها و برچسب‌ها برای فیلتر
    categories = BlogCategory.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'current_status': status,
        'current_category': category,
        'current_tag': tag,
        'current_sort': sort,
        'search_query': search,
        'total_posts': posts.count(),
    }
    return render(request, 'blog/admin/list.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_create(request):
    """ساخت بلاگ جدید"""
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.live = False  # Start as draft

            messages.success(request, 'مقاله بلاگ با موفقیت ایجاد شد.')
            return redirect('blog:admin_list')
        else:
            # نمایش خطاهای فرم
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = BlogForm()

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'blog/admin/create.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_edit(request, pk):
    """ویرایش بلاگ"""
    post = get_object_or_404(BlogPage, pk=pk)
    
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            form.save_m2m()
            
            messages.success(request, 'مقاله بلاگ با موفقیت ویرایش شد.')
            return redirect('blog:admin_list')
    else:
        form = BlogForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'blog/admin/edit.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_delete(request, pk):
    """حذف بلاگ"""
    post = get_object_or_404(BlogPage, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'مقاله بلاگ با موفقیت حذف شد.')
        return redirect('blog:admin_list')
    return render(request, 'blog/admin/delete.html', {'post': post})


@login_required
@user_passes_test(lambda u: u.is_staff)
@csrf_exempt
def auto_save(request, pk):
    """ذخیره خودکار پیش‌نویس"""
    post = get_object_or_404(BlogPage, pk=pk)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')
            if content is not None:
                post.body = content
                post.save(update_fields=['body'])
                return JsonResponse({
                    'status': 'ok',
                    'message': 'پیش‌نویس با موفقیت ذخیره شد'
                })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'داده نامعتبر'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'متد نامعتبر'}, status=405)


@login_required
@user_passes_test(lambda u: u.is_staff)
@csrf_exempt
def upload_media(request):
    """آپلود فایل در کتابخانه رسانه"""
    if request.method == 'POST':
        if not request.FILES.get('file'):
            return JsonResponse({'success': 0, 'message': 'فایلی ارسال نشده است.'}, status=400)
        
        file = request.FILES['file']
        
        # Use Wagtail's image system
        from wagtail.images.models import Image
        try:
            image = Image.objects.create(
                title=file.name,
                file=file,
                uploaded_by_user=request.user
            )
            
            return JsonResponse({
                'success': 1,
                'file': {
                    'url': image.file.url,
                    'id': image.id,
                    'name': image.file.name,
                    'media_type': 'image',
                    'size': image.file.size,
                    'alt': image.title,
                }
            })
        except Exception as e:
            return JsonResponse({'success': 0, 'message': f'خطا در آپلود: {str(e)}'}, status=400)
    
    return JsonResponse({'success': 0, 'message': 'متد نامعتبر است.'}, status=405)


@login_required
@user_passes_test(lambda u: u.is_staff)
def media_library_api(request):
    """API کتابخانه رسانه"""
    search = request.GET.get('search')
    
    from wagtail.images.models import Image
    images = Image.objects.all().order_by('-created_at')
    
    if search:
        images = images.filter(title__icontains=search)
    
    images = images[:50]
    
    data = []
    for image in images:
        data.append({
            'id': image.id,
            'url': image.file.url,
            'name': image.title,
            'media_type': 'image',
            'size': image.file.size,
            'created_at': image.created_at.strftime('%Y-%m-%d %H:%M'),
            'alt': image.title,
        })
    
    return JsonResponse({'success': 1, 'data': data})


@login_required
@user_passes_test(lambda u: u.is_staff)
@csrf_exempt
def delete_media(request, pk):
    """حذف فایل از کتابخانه رسانه"""
    from wagtail.images.models import Image
    media = get_object_or_404(Image, pk=pk)
    if request.method == 'POST':
        media.delete()
        return JsonResponse({'success': 1, 'message': 'فایل با موفقیت حذف شد'})
    return JsonResponse({'success': 0, 'message': 'متد نامعتبر'}, status=405)