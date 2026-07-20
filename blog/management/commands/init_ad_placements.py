from django.core.management.base import BaseCommand
from blog.models import AdPlacement


class Command(BaseCommand):
    help = 'Initialize default ad placements'

    def handle(self, *args, **options):
        placements_data = [
            {
                'name': 'Header Top',
                'slug': 'header-top',
                'placement_code': 'header_top',
                'description': 'بالای هدر سایت'
            },
            {
                'name': 'Header Bottom',
                'slug': 'header-bottom',
                'placement_code': 'header_bottom',
                'description': 'زیر منوی اصلی'
            },
            {
                'name': 'Sidebar Top',
                'slug': 'sidebar-top',
                'placement_code': 'sidebar_top',
                'description': 'ابتدای سایدبار'
            },
            {
                'name': 'Sidebar Sticky',
                'slug': 'sidebar-sticky',
                'placement_code': 'sidebar_sticky',
                'description': 'سایدبار چسبان'
            },
            {
                'name': 'In Article',
                'slug': 'in-article',
                'placement_code': 'in_article',
                'description': 'داخل مقاله'
            },
            {
                'name': 'Before Related',
                'slug': 'before-related',
                'placement_code': 'before_related',
                'description': 'قبل از مطالب مرتبط'
            },
            {
                'name': 'Before Comments',
                'slug': 'before-comments',
                'placement_code': 'before_comments',
                'description': 'قبل از نظرات'
            },
            {
                'name': 'Footer Mobile',
                'slug': 'footer-mobile',
                'placement_code': 'footer_mobile',
                'description': 'بنر پایین موبایل'
            },
            {
                'name': 'Popup',
                'slug': 'popup',
                'placement_code': 'popup',
                'description': 'پاپ‌آپ'
            },
            {
                'name': 'Native Product',
                'slug': 'native-product',
                'placement_code': 'native_product',
                'description': 'محصول داخل مقاله'
            },
            {
                'name': 'Sponsored Box',
                'slug': 'sponsored-box',
                'placement_code': 'sponsored_box',
                'description': 'باکس اسپانسر'
            },
        ]

        created_count = 0
        updated_count = 0

        for placement_data in placements_data:
            placement, created = AdPlacement.objects.get_or_create(
                placement_code=placement_data['placement_code'],
                defaults={
                    'name': placement_data['name'],
                    'slug': placement_data['slug'],
                    'description': placement_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {placement.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {placement.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} created, {updated_count} already exist'
            )
        )
