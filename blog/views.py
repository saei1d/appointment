from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from .models import Blog
from .forms import BlogForm


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_list(request):
    posts = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog/list.html', {'posts': posts})


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if not post.slug:
                post.slug = slugify(post.title, allow_unicode=True)
                counter = 1
                original_slug = post.slug
                while Blog.objects.filter(slug=post.slug).exists():
                    post.slug = f'{original_slug}-{counter}'
                    counter += 1
            if post.is_published and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            messages.success(request, 'مقاله بلاگ با موفقیت ایجاد شد.')
            return redirect('blog_list')
    else:
        form = BlogForm()
    return render(request, 'blog/form.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_edit(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.is_published and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            messages.success(request, 'مقاله بلاگ با موفقیت ویرایش شد.')
            return redirect('blog_list')
    else:
        form = BlogForm(instance=post)
    return render(request, 'blog/form.html', {'form': form, 'post': post})


@login_required
@user_passes_test(lambda u: u.is_staff)
def blog_delete(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'مقاله بلاگ با موفقیت حذف شد.')
        return redirect('blog_list')
    return render(request, 'blog/delete.html', {'post': post})
