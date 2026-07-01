from django.shortcuts import get_object_or_404, render
from .models import Blog

def blog_list_public(request):
    posts = Blog.objects.filter(is_published=True).order_by('-published_at', '-created_at')
    return render(request, 'blog/public_list.html', {'posts': posts})

def blog_detail_public(request, slug):
    post = get_object_or_404(Blog, slug=slug, is_published=True)
    return render(request, 'blog/public_detail.html', {'post': post})
