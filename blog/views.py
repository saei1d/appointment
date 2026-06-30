from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from .models import Blog


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_list(request):
    posts = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog/list.html', {'posts': posts})


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        is_published = bool(request.POST.get('is_published'))
        if title:
            slug = slugify(title, allow_unicode=True)
            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while Blog.objects.filter(slug=slug).exists():
                slug = f'{original_slug}-{counter}'
                counter += 1
            post = Blog.objects.create(
                title=title,
                slug=slug,
                content=content,
                author=request.user,
                image=image,
                is_published=is_published,
                published_at=timezone.now() if is_published else None
            )
            messages.success(request, 'مقاله بلاگ با موفقیت ایجاد شد.')
            return redirect('blog_list')
    return render(request, 'blog/form.html')


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_edit(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        post.title = request.POST.get('title', post.title).strip()
        post.content = request.POST.get('content', post.content).strip()
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.is_published = bool(request.POST.get('is_published'))
        if post.is_published and not post.published_at:
            post.published_at = timezone.now()
        if request.POST.get('slug'):
            new_slug = request.POST.get('slug', '').strip()
            if new_slug != post.slug:
                # Check uniqueness
                if not Blog.objects.filter(slug=new_slug).exclude(pk=post.pk).exists():
                    post.slug = new_slug
        post.save()
        messages.success(request, 'مقاله بلاگ با موفقیت ویرایش شد.')
        return redirect('blog_list')
    return render(request, 'blog/form.html', {'post': post})


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_delete(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'مقاله بلاگ با موفقیت حذف شد.')
        return redirect('blog_list')
    return render(request, 'blog/delete.html', {'post': post})
