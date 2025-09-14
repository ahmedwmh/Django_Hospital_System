from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import City, Center, Doctor, Staff, Medicine, Disease

User = get_user_model()


class CityModelTest(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            name='Test City',
            state='Test State',
            country='Test Country'
        )

    def test_city_creation(self):
        self.assertEqual(self.city.name, 'Test City')
        self.assertEqual(self.city.state, 'Test State')
        self.assertEqual(self.city.country, 'Test Country')

    def test_city_str(self):
        expected = "Test City, Test State"
        self.assertEqual(str(self.city), expected)


class CenterModelTest(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            name='Test City',
            state='Test State',
            country='Test Country'
        )
        self.center = Center.objects.create(
            name='Test Center',
            city=self.city,
            address='123 Test Street',
            phone_number='+1234567890',
            email='test@center.com'
        )

    def test_center_creation(self):
        self.assertEqual(self.center.name, 'Test Center')
        self.assertEqual(self.center.city, self.city)
        self.assertTrue(self.center.is_active)

    def test_center_str(self):
        expected = "Test Center - Test City"
        self.assertEqual(str(self.center), expected)


class DoctorModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='doctor@example.com',
            username='doctor',
            password='testpass123',
            first_name='Dr. Test',
            last_name='Doctor',
            role='DOCTOR'
        )
        self.city = City.objects.create(
            name='Test City',
            state='Test State',
            country='Test Country'
        )
        self.center = Center.objects.create(
            name='Test Center',
            city=self.city,
            address='123 Test Street',
            phone_number='+1234567890'
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            center=self.center,
            specialization='CARDIOLOGY',
            license_number='LIC123456',
            experience_years=5,
            consultation_fee=1000.00
        )

    def test_doctor_creation(self):
        self.assertEqual(self.doctor.user, self.user)
        self.assertEqual(self.doctor.center, self.center)
        self.assertEqual(self.doctor.specialization, 'CARDIOLOGY')
        self.assertTrue(self.doctor.is_available)

    def test_doctor_str(self):
        expected = "Dr. Dr. Test Doctor - Cardiology"
        self.assertEqual(str(self.doctor), expected)


class MedicineModelTest(TestCase):
    def setUp(self):
        self.medicine = Medicine.objects.create(
            name='Test Medicine',
            generic_name='Test Generic',
            dosage_form='tablet',
            strength='500mg',
            manufacturer='Test Pharma',
            side_effects='Test side effects',
            is_prescription_required=True
        )

    def test_medicine_creation(self):
        self.assertEqual(self.medicine.name, 'Test Medicine')
        self.assertEqual(self.medicine.generic_name, 'Test Generic')
        self.assertTrue(self.medicine.is_prescription_required)
        self.assertTrue(self.medicine.is_active)

    def test_medicine_str(self):
        expected = "Test Medicine (500mg)"
        self.assertEqual(str(self.medicine), expected)


class DiseaseModelTest(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(
            name='Test Disease',
            category='CHRONIC',
            description='Test description',
            symptoms='Test symptoms',
            icd_code='T00'
        )

    def test_disease_creation(self):
        self.assertEqual(self.disease.name, 'Test Disease')
        self.assertEqual(self.disease.category, 'CHRONIC')
        self.assertEqual(self.disease.icd_code, 'T00')
        self.assertTrue(self.disease.is_active)

    def test_disease_str(self):
        expected = "Test Disease (Chronic)"
        self.assertEqual(str(self.disease), expected)


class HospitalAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )
        self.city = City.objects.create(
            name='Test City',
            state='Test State',
            country='Test Country'
        )

    def test_city_list_requires_auth(self):
        url = reverse('city-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_city_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('city-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_city_creation_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('city-list')
        data = {
            'name': 'New City',
            'state': 'New State',
            'country': 'New Country'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_center_creation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('center-list')
        data = {
            'name': 'New Center',
            'city': self.city.id,
            'address': '456 New Street',
            'phone_number': '+1234567890',
            'email': 'new@center.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Center')
