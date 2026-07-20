# blog/forms.py
from django import forms
from .models import BlogPage


class BlogForm(forms.ModelForm):
    slug = forms.CharField(required=False, widget=forms.TextInput(attrs={'dir': 'ltr', 'placeholder': 'خودکار تولید می‌شود'}))
    excerpt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'خلاصه‌ای کوتاه از مقاله (اختیاری - در صورت خالی بودن خودکار تولید می‌شود)'
        }),
        help_text='در صورت خالی گذاشتن این فیلد، خلاصه به‌صورت خودکار از محتوای مقاله استخراج می‌شود.'
    )

    class Meta:
        model = BlogPage
        fields = ['title', 'slug', 'excerpt', 'body', 'main_image', 'categories', 'tags']
        widgets = {
            'body': forms.Textarea(attrs={'id': 'id_content', 'hidden': True}),
        }
