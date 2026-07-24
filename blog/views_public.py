# blog/views_public.py
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import BlogPage, BlogCategory, BlogPageTag, BlogComment
import re


def blog_home(request):
    """صفحه اصلی مجله"""
    posts = BlogPage.objects.filter(
        live=True
    ).select_related('main_image').prefetch_related('categories', 'tags')

    featured_posts = posts.order_by('-first_published_at')[:5]
    latest_posts = posts.order_by('-first_published_at')[:12]

    categories = BlogCategory.objects.annotate(
        post_count=Count('blog_pages')
    ).filter(post_count__gt=0).order_by('-post_count')[:8]

    random_posts = posts.order_by('?')[:4]

    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'categories': categories,
        'random_posts': random_posts,
        'hero_post': featured_posts[0] if featured_posts else None,
    }
    return render(request, 'blog/home.html', context)


def blog_detail(request, slug):
    """صفحه داخلی مقاله"""
    # ادمین‌ها می‌توانند مقالات draft را هم ببینند
    if request.user.is_authenticated and request.user.is_staff:
        post = get_object_or_404(
            BlogPage.objects.select_related('main_image')
            .prefetch_related('categories', 'tags'),
            slug=slug
        )
    else:
        post = get_object_or_404(
            BlogPage.objects.select_related('main_image')
            .prefetch_related('categories', 'tags'),
            slug=slug,
            live=True
        )

    blocks = []
    toc = []

    # Find related posts using tags first, then categories
    related_posts = BlogPage.objects.filter(
        live=True
    ).exclude(id=post.id)

    if post.tags.exists():
        tag_ids = post.tags.values_list('id', flat=True)
        related_posts = related_posts.filter(tags__id__in=tag_ids)
    elif post.categories.exists():
        category_ids = post.categories.values_list('id', flat=True)
        related_posts = related_posts.filter(categories__id__in=category_ids)
    else:
        related_posts = related_posts.order_by('?')

    related_posts = related_posts.distinct()[:4]

    reading_time = calculate_reading_time(post)
    json_ld = generate_json_ld(post)

    # Get comments for this post
    from .models import BlogComment
    comments = BlogComment.objects.filter(
        post=post,
        is_approved=True,
        parent=None
    ).select_related('user').prefetch_related('replies__user')

    in_article_ads = []
    ad_placements_to_check = ['sidebar_top', 'sidebar_sticky', 'in_article', 'before_related']
    for placement_code in ad_placements_to_check:
        ads = get_valid_ads(placement_code)
        if ads:
            in_article_ads.append({'placement': placement_code, 'ads': ads})

    context = {
        'post': post,
        'blocks': blocks,
        'toc': toc,
        'related_posts': related_posts,
        'reading_time': reading_time,
        'json_ld': json_ld,
        'comments': comments,
        'in_article_ads': {a['placement']: a['ads'] for a in in_article_ads},
    }
    return render(request, 'blog/detail.html', context)


def category_detail(request, slug):
    """نمایش مقالات یک دسته‌بندی"""
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPage.objects.filter(
        categories=category,
        live=True
    ).order_by('-first_published_at')

    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })


def tag_detail(request, slug):
    """نمایش مقالات یک برچسب"""
    from taggit.models import Tag
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPage.objects.filter(
        tags=tag,
        live=True
    ).order_by('-first_published_at')

    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/tag.html', {
        'tag': tag,
        'page_obj': page_obj,
    })


def blog_search(request):
    """جستجوی مقالات"""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')

    if query:
        posts = BlogPage.objects.filter(
            live=True
        ).filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(body__icontains=query)
        )
        
        if category_slug:
            posts = posts.filter(categories__slug=category_slug)
        
        posts = posts.distinct().order_by('-first_published_at')
    else:
        posts = BlogPage.objects.none()

    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = BlogCategory.objects.annotate(
        post_count=Count('blog_pages')
    ).filter(post_count__gt=0).order_by('-post_count')[:10]

    return render(request, 'blog/search.html', {
        'query': query,
        'page_obj': page_obj,
        'total_results': posts.count(),
        'categories': categories,
    })


def calculate_reading_time(post):
    """محاسبه زمان مطالعه"""
    word_count = 0
    if post.body:
        for block in post.body:
            if block.block_type == 'paragraph':
                # Extract text from RichTextBlock
                import re
                text = re.sub(r'<[^>]+>', '', str(block.value))
                word_count += len(text.split())
            elif block.block_type == 'heading':
                word_count += len(str(block.value).split())
            elif block.block_type == 'colored_text':
                import re
                text = re.sub(r'<[^>]+>', '', str(block.value.get('text', '')))
                word_count += len(text.split())
            elif block.block_type == 'quote':
                word_count += len(str(block.value).split())
            elif block.block_type == 'list':
                for item in block.value:
                    word_count += len(str(item).split())
    return max(1, word_count // 200)


def extract_toc(blocks):
    """استخراج فهرست مطالب از بلاک‌های محتوا"""
    toc = []
    if not blocks:
        return toc

    for block in blocks:
        if block.get('type') == 'header':
            data = block.get('data', {})
            level = data.get('level', 2)
            text = data.get('text', '')
            if text and level <= 3:
                clean_text = re.sub(r'<[^>]+>', '', text)
                header_id = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF\-]', '-', clean_text.lower())
                header_id = re.sub(r'-+', '-', header_id).strip('-')
                toc.append({
                    'id': header_id,
                    'text': clean_text,
                    'level': level,
                })
    return toc


def generate_json_ld(post):
    """تولید JSON-LD"""
    json_ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.excerpt or post.title,
        "datePublished": post.first_published_at.isoformat() if post.first_published_at else '',
        "dateModified": post.last_published_at.isoformat() if post.last_published_at else '',
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"/blog/post/{post.slug}/"
        }
    }

    if post.main_image:
        json_ld["image"] = post.main_image.file.url

    return json_ld


def get_valid_ads(placement_code):
    """دریافت تبلیغات معتبر برای یک جایگاه"""
    from .models import AdPlacement, Ad
    now = timezone.now()
    try:
        placement = AdPlacement.objects.get(placement_code=placement_code, is_active=True)
    except AdPlacement.DoesNotExist:
        return []

    return list(
        Ad.objects.filter(
            placement=placement,
            is_active=True,
            start_date__lte=now,
        ).exclude(
            end_date__isnull=False, end_date__lt=now
        ).order_by('-priority')[:1]
    )


def instant_search_api(request):
    """API برای جستجوی آنی"""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    
    results = []
    
    if query:
        posts = BlogPage.objects.filter(
            live=True
        ).filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(body__icontains=query)
        )
        
        if category_slug:
            posts = posts.filter(categories__slug=category_slug)
        
        posts = posts.select_related('main_image').prefetch_related('categories', 'tags')[:10]
        
        for post in posts:
            results.append({
                'id': post.id,
                'title': post.title,
                'excerpt': post.excerpt[:150] if post.excerpt else '',
                'slug': post.slug,
                'image': post.main_image.file.url if post.main_image else None,
                'categories': [{'name': cat.name, 'slug': cat.slug} for cat in post.categories.all()],
                'date': post.first_published_at.strftime('%d %B %Y') if post.first_published_at else '',
            })
    
    return JsonResponse({'results': results})


@login_required
@require_POST
def add_comment(request, slug):
    """افزودن نظر به مقاله"""
    post = get_object_or_404(BlogPage, slug=slug, live=True)
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not content:
        return JsonResponse({'success': False, 'error': 'محتوای نظر نمی‌تواند خالی باشد'})
    
    # Check if user is trying to reply (only admin can reply)
    parent = None
    if parent_id:
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'فقط ادمین می‌تواند پاسخ دهد'})
        try:
            parent = BlogComment.objects.get(id=parent_id, post=post)
        except BlogComment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'نظر اصلی یافت نشد'})
    
    # Create comment
    comment = BlogComment.objects.create(
        post=post,
        user=request.user,
        parent=parent,
        content=content,
        is_approved=True  # Auto-approve for now
    )
    
    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'user': comment.user.get_full_name(),
            'created_at': comment.created_at.strftime('%d %B %Y - %H:%M'),
            'is_admin_reply': comment.is_admin_reply,
            'is_reply': comment.is_reply,
            'parent_id': parent_id
        }
    })
