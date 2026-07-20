# blog/templatetags/blog_tags.py
from django import template
from django.utils.safestring import mark_safe
from django.utils import timezone
import json
import re

register = template.Library()


@register.filter
def render_blocks(blocks):
    """ردر کامل تمام بلاک‌های Editor.js"""
    if not blocks:
        return ''

    if isinstance(blocks, dict):
        blocks = blocks.get('blocks', [])

    html_parts = []
    for block in blocks:
        html = _render_single_block(block)
        if html:
            html_parts.append(html)

    return mark_safe('\n'.join(html_parts))


@register.inclusion_tag('blog/public/_block.html', takes_context=False)
def render_single_block(block):
    """ردر یک بلاک واحد - برای استفاده در حلقه"""
    html = _render_single_block(block)
    return {'block_html': html}


def _render_single_block(block):
    btype = block.get('type', '')
    data = block.get('data', {})

    if btype == 'html':
        html = data.get('html', '')
        if html:
            return f'<div class="prose prose-lg max-w-none">{html}</div>'
        return ''

    if btype == 'header':
        level = data.get('level', 2)
        text = data.get('text', '')
        if not text:
            return ''
        clean = re.sub(r'<[^>]+>', '', text)
        header_id = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF\-]', '-', clean.lower())
        header_id = re.sub(r'-+', '-', header_id).strip('-')
        return f'<h{level} id="{header_id}" class="font-bold mt-8 mb-4 text-gray-900">{text}</h{level}>'

    elif btype == 'paragraph':
        text = data.get('text', '')
        if not text or text == '<br>':
            return ''
        return f'<p class="text-lg leading-relaxed mb-6 text-gray-700">{text}</p>'

    elif btype == 'image':
        file_data = data.get('file', {})
        url = file_data.get('url', '') if isinstance(file_data, dict) else ''
        caption = data.get('caption', '')
        with_border = data.get('withBorder', False)
        stretched = data.get('stretched', False)
        with_background = data.get('withBackground', False)

        border_class = 'border border-gray-200' if with_border else ''
        bg_class = 'bg-gray-100 p-4' if with_background else ''
        width_class = 'w-full' if stretched else ''

        img = f'<img src="{url}" alt="{caption}" class="rounded-xl {width_class} {border_class}" loading="lazy">'
        if caption:
            img += f'<figcaption class="text-center text-sm text-gray-500 mt-2">{caption}</figcaption>'
        return f'<figure class="my-6 {bg_class}">{img}</figure>'

    elif btype == 'list':
        style = data.get('style', 'unordered')
        items = data.get('items', [])
        if not items:
            return ''
        tag = 'ul' if style == 'unordered' else 'ol'
        list_class = 'list-disc pr-6 space-y-2' if style == 'unordered' else 'list-decimal pr-6 space-y-2'
        items_html = '\n'.join(f'<li class="text-gray-700">{item}</li>' for item in items)
        return f'<{tag} class="{list_class} my-4">{items_html}</{tag}>'

    elif btype == 'table':
        content = data.get('content', [])
        if not content:
            return ''
        header_row = content[0] if content else []
        body_rows = content[1:] if len(content) > 1 else []

        thead = ''
        if header_row:
            cells = ''.join(f'<th class="px-4 py-3 bg-pink-50 text-pink-700 font-bold border border-gray-200 text-right">{c}</th>' for c in header_row)
            thead = f'<thead><tr>{cells}</tr></thead>'

        tbody = ''
        for row in body_rows:
            cells = ''.join(f'<td class="px-4 py-3 border border-gray-200 text-right">{c}</td>' for c in row)
            tbody += f'<tr>{cells}</tr>'

        return f'<div class="overflow-x-auto my-6"><table class="w-full border-collapse"><thead>{thead}</thead><tbody class="divide-y divide-gray-200">{tbody}</tbody></table></div>'

    elif btype == 'code':
        code = data.get('code', '')
        if not code:
            return ''
        return f'<div class="my-6"><pre class="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-x-auto text-sm" dir="ltr"><code>{code}</code></pre></div>'

    elif btype == 'quote':
        text = data.get('text', '')
        caption = data.get('caption', '')
        alignment = data.get('alignment', 'left')
        text_align = 'text-left' if alignment == 'left' else 'text-right'
        caption_html = f'<footer class="text-sm text-gray-500 mt-2">— {caption}</footer>' if caption else ''
        return f'<blockquote class="border-r-4 border-[#FB9D90] bg-gradient-to-l from-pink-50 to-white p-5 rounded-xl my-6"><p class="text-lg text-gray-800 italic {text_align}">{text}</p>{caption_html}</blockquote>'

    elif btype == 'delimiter':
        return '<hr class="my-8 border-t-2 border-gray-200">'

    elif btype == 'embed':
        service = data.get('service', '')
        source = data.get('source', '')
        caption = data.get('caption', '')
        if not source:
            return ''
        if 'youtube' in service or 'youtu.be' in service:
            embed_url = source.replace('watch?v=', 'embed/').replace('youtube.com/', 'youtube.com/embed/')
            return f'<div class="my-6 aspect-video"><iframe src="{embed_url}" class="w-full h-full rounded-xl" frameborder="0" allowfullscreen></iframe></div>'
        return f'<div class="my-6"><a href="{source}" target="_blank" class="text-pink-600 hover:underline">{caption or source}</a></div>'

    elif btype == 'warning':
        title = data.get('title', 'هشدار')
        message = data.get('message', '')
        return f'<div class="bg-amber-50 border-r-4 border-amber-400 p-4 rounded-xl my-6"><div class="font-bold text-amber-800 mb-1">{title}</div><div class="text-amber-700">{message}</div></div>'

    elif btype == 'checklist':
        items = data.get('items', [])
        if not items:
            return ''
        html_items = ''
        for item in items:
            checked = 'checked' if item.get('checked') else ''
            text = item.get('text', '')
            html_items += f'<li class="flex items-center gap-2 py-1"><input type="checkbox" {checked} class="accent-pink-500 w-4 h-4" disabled><span class="text-gray-700">{text}</span></li>'
        return f'<ul class="my-4 space-y-1">{html_items}</ul>'

    elif btype == 'marker':
        text = data.get('text', '')
        return f'<mark class="bg-yellow-200 px-1 rounded">{text}</mark>'

    elif btype == 'inlineCode':
        code = data.get('code', '')
        return f'<code class="bg-gray-100 text-pink-600 px-2 py-0.5 rounded text-sm" dir="ltr">{code}</code>'

    return ''


@register.simple_tag(takes_context=True)
def render_ad(context, placement_code, css_class=''):
    """
    ردر تبلیغ برای یک جایگاه مشخص.
    Usage: {% render_ad "header_top" %}
    """
    from ..models import AdPlacement, Ad
    now = timezone.now()

    try:
        placement = AdPlacement.objects.get(placement_code=placement_code, is_active=True)
    except AdPlacement.DoesNotExist:
        return ''

    ad = Ad.objects.filter(
        placement=placement,
        is_active=True,
        start_date__lte=now,
    ).exclude(
        end_date__isnull=False, end_date__lt=now
    ).order_by('-priority').first()

    if not ad:
        return ''

    request = context.get('request')
    is_mobile = False
    if request:
        ua = request.META.get('HTTP_USER_AGENT', '').lower()
        is_mobile = any(x in ua for x in ['mobile', 'android', 'iphone', 'ipad'])

    image_url = ''
    if is_mobile and ad.image_mobile:
        image_url = ad.image_mobile.url
    elif ad.image_desktop:
        image_url = ad.image_desktop.url

    if not image_url:
        return ''

    tag = context.get('request', None)
    impression_count = ad.impression_count + 1
    Ad.objects.filter(pk=ad.pk).update(impression_count=impression_count)

    target_attr = 'target="_blank" rel="noopener noreferrer"' if ad.link_url else ''
    link_start = f'<a href="{ad.link_url}" {target_attr} class="block">' if ad.link_url else ''
    link_end = '</a>' if ad.link_url else ''

    close_button = ''
    if placement_code == 'header_top':
        close_button = '''<button onclick="this.parentElement.style.display='none'" class="ad-close">×</button>'''

    html = f'''<div class="ad-container {css_class}">
        {close_button}
        {link_start}<img src="{image_url}" alt="{ad.title}" loading="lazy">{link_end}
    </div>'''

    return mark_safe(html)


@register.simple_tag(takes_context=True)
def render_ad_by_code(context, placement_code, css_class=''):
    """alias for render_ad"""
    return render_ad(context, placement_code, css_class)


@register.filter
def to_jalali(value):
    """تبدیل ساده تاریخ به فرمت خوانا"""
    if not value:
        return ''
    try:
        return value.strftime('%Y/%m/%d - %H:%M')
    except Exception:
        return str(value)
