from django import forms
from .models import Blog
from ckeditor.widgets import CKEditorWidget


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'slug', 'content', 'image', 'is_published']
        widgets = {
            'content': CKEditorWidget(),
        }
