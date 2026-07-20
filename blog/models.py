# blog/models.py

from django.db import models
from django.utils import timezone
from django.conf import settings

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from taggit.models import TaggedItemBase

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


# ========================================
# Tags
# ========================================

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "BlogPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


# ========================================
# Categories
# ========================================

@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(unique=True, verbose_name="اسلاگ")

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        verbose_name = "دسته‌بندی بلاگ"
        verbose_name_plural = "دسته‌بندی‌های بلاگ"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ========================================
# Blog Page
# ========================================

class BlogPage(Page):

    main_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="تصویر اصلی",
    )

    excerpt = models.TextField(
        blank=True,
        verbose_name="خلاصه مقاله",
    )

    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="title", icon="title")),
        ('paragraph', blocks.RichTextBlock(icon="pilcrow")),
        ('html', blocks.RawHTMLBlock(icon="code", label="HTML سفارشی")),
        ('image', ImageChooserBlock(icon="image")),
        ('quote', blocks.BlockQuoteBlock(icon="openquote")),
        ('list', blocks.ListBlock(blocks.CharBlock(icon="list"), icon="list")),
        ('colored_text', blocks.StructBlock([
            ('text', blocks.RichTextBlock(icon="pilcrow")),
            ('color', blocks.ChoiceBlock(choices=[
                ('red', 'قرمز'),
                ('blue', 'آبی'),
                ('green', 'سبز'),
                ('yellow', 'زرد'),
                ('purple', 'بنفش'),
                ('pink', 'صورتی'),
                ('orange', 'نارنجی'),
                ('gray', 'خاکستری'),
                ('black', 'مشکی'),
            ], icon="color")),
            ('background_color', blocks.ChoiceBlock(choices=[
                ('', 'بدون پس‌زمینه'),
                ('red', 'قرمز'),
                ('blue', 'آبی'),
                ('green', 'سبز'),
                ('yellow', 'زرد'),
                ('purple', 'بنفش'),
                ('pink', 'صورتی'),
                ('orange', 'نارنجی'),
                ('gray', 'خاکستری'),
                ('light', 'روشن'),
            ], icon="color", required=False)),
        ], icon="color")),
        ('table', blocks.StructBlock([
            ('rows', blocks.StreamBlock([
                ('row', blocks.StreamBlock([
                    ('cell', blocks.CharBlock(icon="table")),
                ], icon="table")),
            ], icon="table")),
        ], icon="table")),
        ('button', blocks.StructBlock([
            ('text', blocks.CharBlock(icon="title")),
            ('link', blocks.URLBlock(icon="link")),
            ('style', blocks.ChoiceBlock(choices=[
                ('primary', 'اصلی'),
                ('secondary', 'ثانویه'),
                ('outline', 'بی‌حاشیه'),
            ], icon="color")),
        ], icon="link")),
        ('alert', blocks.StructBlock([
            ('text', blocks.RichTextBlock(icon="pilcrow")),
            ('type', blocks.ChoiceBlock(choices=[
                ('info', 'اطلاعات'),
                ('warning', 'هشدار'),
                ('success', 'موفقیت'),
                ('error', 'خطا'),
            ], icon="warning")),
        ], icon="warning")),
        ('divider', blocks.StructBlock([
            ('style', blocks.ChoiceBlock(choices=[
                ('solid', 'توپر'),
                ('dashed', 'خط‌چین'),
                ('dotted', 'نقطه‌چین'),
            ], icon="separator")),
        ], icon="separator")),
    ], blank=True, verbose_name="محتوای مقاله")

    categories = models.ManyToManyField(
        BlogCategory,
        blank=True,
        related_name="blog_pages",
        verbose_name="دسته‌بندی‌ها",
    )

    tags = ClusterTaggableManager(
        through=BlogPageTag,
        blank=True,
        verbose_name="برچسب‌ها",
    )

    search_fields = Page.search_fields + [
        index.SearchField("title"),
        index.SearchField("excerpt"),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("main_image"),
        FieldPanel("excerpt"),
        FieldPanel("body"),
        FieldPanel("categories"),
        FieldPanel("tags"),
    ]


    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"


# ========================================
# Advertisement Placement
# ========================================

class AdPlacement(models.Model):

    PLACEMENT_CHOICES = [
        ("header_top", "بالای هدر"),
        ("header_bottom", "زیر هدر"),
        ("sidebar_top", "ابتدای سایدبار"),
        ("sidebar_sticky", "سایدبار چسبان"),
        ("in_article", "داخل مقاله"),
        ("before_related", "قبل از مطالب مرتبط"),
        ("before_comments", "قبل از نظرات"),
        ("footer_mobile", "بنر پایین موبایل"),
        ("popup", "پاپ‌آپ"),
        ("native_product", "محصول داخل مقاله"),
        ("sponsored_box", "باکس اسپانسر"),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    placement_code = models.CharField(
        max_length=50,
        choices=PLACEMENT_CHOICES,
        unique=True,
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "جایگاه تبلیغات"
        verbose_name_plural = "جایگاه‌های تبلیغات"

    def __str__(self):
        return self.name


# ========================================
# Advertisement
# ========================================

class Ad(models.Model):

    title = models.CharField(max_length=200)

    placement = models.ForeignKey(
        AdPlacement,
        on_delete=models.CASCADE,
        related_name="ads",
    )

    image_desktop = models.ImageField(
        upload_to="ads/desktop/%Y/%m/",
    )

    image_mobile = models.ImageField(
        upload_to="ads/mobile/%Y/%m/",
        blank=True,
        null=True,
    )

    link_url = models.URLField(blank=True)

    start_date = models.DateTimeField()

    end_date = models.DateTimeField(
        blank=True,
        null=True,
    )

    priority = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    impression_count = models.PositiveIntegerField(default=0)

    click_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        verbose_name = "تبلیغ"
        verbose_name_plural = "تبلیغات"

    def __str__(self):
        return self.title

    @property
    def is_valid_now(self):
        now = timezone.now()

        if not self.is_active:
            return False

        if self.start_date and now < self.start_date:
            return False

        if self.end_date and now > self.end_date:
            return False

        return True


# ========================================
# Blog Comments
# ========================================

class BlogComment(models.Model):
    post = models.ForeignKey(
        BlogPage,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="مقاله"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_comments',
        verbose_name="کاربر"
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="پاسخ به"
    )
    
    content = models.TextField(verbose_name="محتوای نظر")
    
    is_approved = models.BooleanField(
        default=True,
        verbose_name="تایید شده"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی"
    )

    class Meta:
        verbose_name = "نظر بلاگ"
        verbose_name_plural = "نظرات بلاگ"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.post.title[:30]}"

    @property
    def is_admin_reply(self):
        """Check if this comment is an admin reply"""
        return self.parent is not None and self.user.is_staff

    @property
    def is_reply(self):
        """Check if this is a reply to another comment"""
        return self.parent is not None

