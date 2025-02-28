from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.users.models import User
from .models import Provider, Service, Appointment


class ProviderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            phone='09123456789',
            fullname='Test Provider',
            user_type='provider'
        )
        self.provider = Provider.objects.create(
            user=self.user,
            business_name='Test Beauty Salon',
            address='Test Address',
            is_verified=True
        )

    def test_provider_creation(self):
        self.assertEqual(self.provider.business_name, 'Test Beauty Salon')
        self.assertEqual(self.provider.user.fullname, 'Test Provider')
        self.assertTrue(self.provider.is_verified)


class ServiceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            phone='09123456789',
            fullname='Test Provider',
            user_type='provider'
        )
        self.provider = Provider.objects.create(
            user=self.user,
            business_name='Test Beauty Salon',
            address='Test Address'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            name='Haircut',
            price=100.00,
            duration=30
        )

    def test_service_creation(self):
        self.assertEqual(self.service.name, 'Haircut')
        self.assertEqual(self.service.provider.business_name, 'Test Beauty Salon')
        self.assertEqual(self.service.price, 100.00)
        self.assertEqual(self.service.duration, 30)


class AppointmentModelTest(TestCase):
    def setUp(self):
        self.provider_user = User.objects.create(
            phone='09123456789',
            fullname='Test Provider',
            user_type='provider'
        )
        self.client_user = User.objects.create(
            phone='09987654321',
            fullname='Test Client'
        )
        self.provider = Provider.objects.create(
            user=self.provider_user,
            business_name='Test Beauty Salon',
            address='Test Address'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            name='Haircut',
            price=100.00,
            duration=30
        )
        self.appointment = Appointment.objects.create(
            user=self.client_user,
            service=self.service,
            date='2023-06-01',
            start_time='10:00:00',
            end_time='10:30:00',
            status='confirmed'
        )

    def test_appointment_creation(self):
        self.assertEqual(self.appointment.user.fullname, 'Test Client')
        self.assertEqual(self.appointment.service.name, 'Haircut')
        self.assertEqual(self.appointment.status, 'confirmed')


class ProviderAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            phone='09123456789',
            fullname='Test Provider',
            user_type='provider'
        )
        self.provider_data = {
            'user': self.user.id,
            'business_name': 'Test Beauty Salon',
            'address': 'Test Address',
            'is_verified': True
        }
        self.url = reverse('provider-list')

    def test_create_provider(self):
        response = self.client.post(self.url, self.provider_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(Provider.objects.get().business_name, 'Test Beauty Salon')