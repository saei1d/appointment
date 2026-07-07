from django.core.management.base import BaseCommand
from subscription.models import Plan


class Command(BaseCommand):
    help = 'Create three beauty salon subscription plans with feminine names'

    def handle(self, *args, **options):
        # Plan 1: گلبرگ (Petal) - Basic plan: booking + SMS
        plan1, created = Plan.objects.get_or_create(
            name='گلبرگ',
            defaults={
                'description': 'پلن پایه برای شروع کار سالن زیبایی. شامل نوبت‌دهی و ارسال پیامک.',
                'price': 199000,
                'duration_days': 30,
                'can_accept_deposits': False,
                'can_use_sms': True,
                'can_manage_products': False,
                'can_view_statistics': False,
                'can_create_discounts': False,
                'can_use_loyalty': False,
                'can_show_portfolio': False,
                'can_have_gallery': False,
                'can_show_on_homepage': False,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'پلن "{plan1.name}" ایجاد شد'))
        else:
            self.stdout.write(self.style.WARNING(f'پلن "{plan1.name}" قبلاً وجود داشته است'))

        # Plan 2: نیلوفر (Lotus) - Premium: portfolio + gallery + monthly reports
        plan2, created = Plan.objects.get_or_create(
            name='نیلوفر',
            defaults={
                'description': 'پلن حرفه‌ای برای سالن‌های زیبایی با نمونه کار و گالری تصاویر.',
                'price': 499000,
                'duration_days': 30,
                'can_accept_deposits': True,
                'can_use_sms': True,
                'can_manage_products': True,
                'can_view_statistics': True,
                'can_create_discounts': True,
                'can_use_loyalty': False,
                'can_show_portfolio': True,
                'can_have_gallery': True,
                'can_show_on_homepage': False,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'پلن "{plan2.name}" ایجاد شد'))
        else:
            self.stdout.write(self.style.WARNING(f'پلن "{plan2.name}" قبلاً وجود داشته است'))

        # Plan 3: سلطانة (Sultana) - VIP: all features + city homepage display
        plan3, created = Plan.objects.get_or_create(
            name='سلطانة',
            defaults={
                'description': 'پلن ویژه برای سالن‌های لوکس با نمایش در صفحه اول شهر.',
                'price': 999000,
                'duration_days': 30,
                'can_accept_deposits': True,
                'can_use_sms': True,
                'can_manage_products': True,
                'can_view_statistics': True,
                'can_create_discounts': True,
                'can_use_loyalty': True,
                'can_show_portfolio': True,
                'can_have_gallery': True,
                'can_show_on_homepage': True,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'پلن "{plan3.name}" ایجاد شد'))
        else:
            self.stdout.write(self.style.WARNING(f'پلن "{plan3.name}" قبلاً وجود داشته است'))

        self.stdout.write(self.style.SUCCESS('پلن‌های اشتراک با موفقیت ایجاد شدند!'))
