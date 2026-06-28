from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = [('provider','0001_initial')]
    operations = [
        migrations.CreateModel(name='Plan', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),('name', models.CharField(max_length=100)),('description', models.TextField(blank=True)),('price', models.DecimalField(decimal_places=0, max_digits=12)),('duration_days', models.PositiveIntegerField(default=30)),('can_accept_deposits', models.BooleanField(default=False)),('can_use_sms', models.BooleanField(default=False)),('can_manage_products', models.BooleanField(default=False)),('can_view_statistics', models.BooleanField(default=False)),('can_create_discounts', models.BooleanField(default=False)),('can_use_loyalty', models.BooleanField(default=False)),('is_active', models.BooleanField(default=True)),('created_at', models.DateTimeField(auto_now_add=True)),('updated_at', models.DateTimeField(auto_now=True))]),
        migrations.CreateModel(name='Subscription', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),('start_date', models.DateField(default=django.utils.timezone.localdate)),('end_date', models.DateField()),('is_active', models.BooleanField(default=True)),('created_at', models.DateTimeField(auto_now_add=True)),('updated_at', models.DateTimeField(auto_now=True)),('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='subscription.plan')),('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='provider.provider'))], options={'ordering': ('-end_date',)}),
    ]
