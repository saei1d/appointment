from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name='Blog', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),('title', models.CharField(max_length=200)),('slug', models.SlugField(unique=True)),('content', models.TextField()),('image', models.ImageField(blank=True, null=True, upload_to='blog_images/')),('is_published', models.BooleanField(default=False)),('published_at', models.DateTimeField(blank=True, null=True)),('created_at', models.DateTimeField(auto_now_add=True)),('updated_at', models.DateTimeField(auto_now=True)),('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to=settings.AUTH_USER_MODEL))])]
