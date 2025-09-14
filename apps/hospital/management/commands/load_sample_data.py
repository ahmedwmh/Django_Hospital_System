from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.hospital.models import City, Center, Doctor, Staff, Medicine, Disease
from apps.patients.models import Patient, PatientDisease, Test, Treatment, TreatmentMedicine, Surgery
from apps.accounts.models import User
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Load sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before loading')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            # Clear data in reverse order of dependencies
            Surgery.objects.all().delete()
            TreatmentMedicine.objects.all().delete()
            Treatment.objects.all().delete()
            Test.objects.all().delete()
            PatientDisease.objects.all().delete()
            Patient.objects.all().delete()
            Staff.objects.all().delete()
            Doctor.objects.all().delete()
            Center.objects.all().delete()
            City.objects.all().delete()
            Disease.objects.all().delete()
            Medicine.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Loading sample data...')

        # Create cities
        cities_data = [
            {'name': 'Mumbai', 'state': 'Maharashtra', 'country': 'India'},
            {'name': 'Delhi', 'state': 'Delhi', 'country': 'India'},
            {'name': 'Bangalore', 'state': 'Karnataka', 'country': 'India'},
            {'name': 'Chennai', 'state': 'Tamil Nadu', 'country': 'India'},
            {'name': 'Kolkata', 'state': 'West Bengal', 'country': 'India'},
        ]
        
        cities = []
        for city_data in cities_data:
            city, created = City.objects.get_or_create(**city_data)
            cities.append(city)
            if created:
                self.stdout.write(f'Created city: {city.name}')

        # Create centers
        centers_data = [
            {'name': 'Apollo Hospital', 'city': cities[0], 'address': '123 Marine Drive, Mumbai', 'phone_number': '+91-22-12345678', 'email': 'mumbai@apollo.com'},
            {'name': 'Fortis Hospital', 'city': cities[1], 'address': '456 Connaught Place, Delhi', 'phone_number': '+91-11-87654321', 'email': 'delhi@fortis.com'},
            {'name': 'Manipal Hospital', 'city': cities[2], 'address': '789 MG Road, Bangalore', 'phone_number': '+91-80-11223344', 'email': 'bangalore@manipal.com'},
            {'name': 'Apollo Hospital', 'city': cities[3], 'address': '321 Anna Salai, Chennai', 'phone_number': '+91-44-55667788', 'email': 'chennai@apollo.com'},
            {'name': 'AMRI Hospital', 'city': cities[4], 'address': '654 Park Street, Kolkata', 'phone_number': '+91-33-99887766', 'email': 'kolkata@amri.com'},
        ]
        
        centers = []
        for center_data in centers_data:
            center, created = Center.objects.get_or_create(**center_data)
            centers.append(center)
            if created:
                self.stdout.write(f'Created center: {center.name}')

        # Create diseases
        diseases_data = [
            {'name': 'Diabetes', 'category': 'CHRONIC', 'description': 'A metabolic disorder', 'symptoms': 'Increased thirst, frequent urination', 'icd_code': 'E11'},
            {'name': 'Hypertension', 'category': 'CHRONIC', 'description': 'High blood pressure', 'symptoms': 'Headaches, shortness of breath', 'icd_code': 'I10'},
            {'name': 'Common Cold', 'category': 'ACUTE', 'description': 'Viral infection of upper respiratory tract', 'symptoms': 'Runny nose, cough, sneezing', 'icd_code': 'J00'},
            {'name': 'Pneumonia', 'category': 'INFECTIOUS', 'description': 'Infection of the lungs', 'symptoms': 'Cough, fever, difficulty breathing', 'icd_code': 'J18'},
            {'name': 'Fracture', 'category': 'ACUTE', 'description': 'Broken bone', 'symptoms': 'Pain, swelling, deformity', 'icd_code': 'S72'},
            {'name': 'Depression', 'category': 'MENTAL', 'description': 'Mental health disorder', 'symptoms': 'Persistent sadness, loss of interest', 'icd_code': 'F32'},
        ]
        
        diseases = []
        for disease_data in diseases_data:
            disease, created = Disease.objects.get_or_create(**disease_data)
            diseases.append(disease)
            if created:
                self.stdout.write(f'Created disease: {disease.name}')

        # Create medicines
        medicines_data = [
            {'name': 'Metformin', 'generic_name': 'Metformin HCl', 'dosage_form': 'tablet', 'strength': '500mg', 'manufacturer': 'Sun Pharma', 'side_effects': 'Nausea, diarrhea', 'is_prescription_required': True},
            {'name': 'Amlodipine', 'generic_name': 'Amlodipine Besylate', 'dosage_form': 'tablet', 'strength': '5mg', 'manufacturer': 'Cipla', 'side_effects': 'Dizziness, swelling', 'is_prescription_required': True},
            {'name': 'Paracetamol', 'generic_name': 'Acetaminophen', 'dosage_form': 'tablet', 'strength': '500mg', 'manufacturer': 'GSK', 'side_effects': 'Rare liver damage', 'is_prescription_required': False},
            {'name': 'Amoxicillin', 'generic_name': 'Amoxicillin', 'dosage_form': 'capsule', 'strength': '250mg', 'manufacturer': 'Dr. Reddy\'s', 'side_effects': 'Diarrhea, nausea', 'is_prescription_required': True},
            {'name': 'Ibuprofen', 'generic_name': 'Ibuprofen', 'dosage_form': 'tablet', 'strength': '400mg', 'manufacturer': 'Pfizer', 'side_effects': 'Stomach upset', 'is_prescription_required': False},
        ]
        
        medicines = []
        for medicine_data in medicines_data:
            medicine, created = Medicine.objects.get_or_create(**medicine_data)
            medicines.append(medicine)
            if created:
                self.stdout.write(f'Created medicine: {medicine.name}')

        # Create doctors
        doctor_specializations = ['CARDIOLOGY', 'NEUROLOGY', 'ONCOLOGY', 'PEDIATRICS', 'GYNECOLOGY', 'ORTHOPEDICS', 'DERMATOLOGY', 'PSYCHIATRY', 'RADIOLOGY', 'ANESTHESIOLOGY', 'EMERGENCY', 'GENERAL']
        
        for i, center in enumerate(centers):
            for j in range(3):  # 3 doctors per center
                doctor_data = {
                    'email': f'doctor{i}{j}@hospital.com',
                    'username': f'doctor{i}{j}',
                    'first_name': f'Dr. {["John", "Jane", "Michael", "Sarah", "David", "Lisa"][j]}',
                    'last_name': f'{["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"][j]}',
                    'phone_number': f'+91-{random.randint(9000000000, 9999999999)}',
                    'role': 'DOCTOR'
                }
                
                user = User.objects.create_user(**doctor_data)
                
                doctor = Doctor.objects.create(
                    user=user,
                    center=center,
                    specialization=random.choice(doctor_specializations),
                    license_number=f'LIC{random.randint(100000, 999999)}',
                    experience_years=random.randint(1, 20),
                    consultation_fee=random.randint(500, 2000),
                    is_available=random.choice([True, True, True, False])  # 75% available
                )
                self.stdout.write(f'Created doctor: {doctor.user.get_full_name()}')

        # Create staff
        departments = ['ADMINISTRATION', 'NURSING', 'LABORATORY', 'PHARMACY', 'RADIOLOGY', 'RECEPTION', 'HOUSEKEEPING', 'SECURITY']
        
        for i, center in enumerate(centers):
            for j in range(5):  # 5 staff per center
                staff_data = {
                    'email': f'staff{i}{j}@hospital.com',
                    'username': f'staff{i}{j}',
                    'first_name': f'{["Alice", "Bob", "Carol", "Dan", "Eve"][j]}',
                    'last_name': f'{["Anderson", "Baker", "Carter", "Davis", "Evans"][j]}',
                    'phone_number': f'+91-{random.randint(9000000000, 9999999999)}',
                    'role': 'STAFF'
                }
                
                user = User.objects.create_user(**staff_data)
                
                staff = Staff.objects.create(
                    user=user,
                    center=center,
                    department=random.choice(departments),
                    employee_id=f'EMP{random.randint(100000, 999999)}',
                    salary=random.randint(20000, 80000),
                    is_active=random.choice([True, True, True, False])  # 75% active
                )
                self.stdout.write(f'Created staff: {staff.user.get_full_name()}')

        # Create patients
        doctors = Doctor.objects.all()
        
        for i in range(50):  # 50 patients
            patient_data = {
                'email': f'patient{i}@example.com',
                'username': f'patient{i}',
                'first_name': f'{["Alex", "Blake", "Casey", "Drew", "Emery"][i % 5]}',
                'last_name': f'{["Taylor", "Miller", "Wilson", "Moore", "Jackson"][i % 5]}',
                'phone_number': f'+91-{random.randint(9000000000, 9999999999)}',
                'role': 'PATIENT'
            }
            
            user = User.objects.create_user(**patient_data)
            
            patient = Patient.objects.create(
                user=user,
                doctor=random.choice(doctors),
                patient_id=f'PAT{str(i+1).zfill(6)}',
                date_of_birth=datetime.now().date() - timedelta(days=random.randint(18*365, 80*365)),
                gender=random.choice(['M', 'F', 'O']),
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', '']),
                address=f'{random.randint(1, 999)} Main Street, City {i+1}',
                emergency_contact_name=f'Emergency Contact {i+1}',
                emergency_contact_phone=f'+91-{random.randint(9000000000, 9999999999)}',
                medical_history=f'Medical history for patient {i+1}',
                allergies=f'Allergies for patient {i+1}' if random.choice([True, False]) else '',
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            self.stdout.write(f'Created patient: {patient.user.get_full_name()}')

        # Create patient diseases
        patients = Patient.objects.all()
        
        for patient in patients:
            # Each patient has 1-3 diseases
            num_diseases = random.randint(1, 3)
            patient_diseases = random.sample(diseases, num_diseases)
            
            for disease in patient_diseases:
                PatientDisease.objects.create(
                    patient=patient,
                    disease=disease,
                    diagnosed_date=datetime.now().date() - timedelta(days=random.randint(1, 365)),
                    status=random.choice(['ACTIVE', 'TREATED', 'CHRONIC', 'CURED']),
                    notes=f'Notes for {disease.name} diagnosis'
                )

        # Create tests
        test_types = ['BLOOD', 'URINE', 'XRAY', 'CT', 'MRI', 'ECG', 'ECHO', 'ULTRASOUND', 'BIOPSY', 'CULTURE']
        
        for patient in patients:
            # Each patient has 2-5 tests
            num_tests = random.randint(2, 5)
            
            for i in range(num_tests):
                disease = random.choice(patient.patient_diseases.all()).disease
                
                test = Test.objects.create(
                    patient=patient,
                    disease=disease,
                    test_name=f'{random.choice(test_types)} Test {i+1}',
                    test_type=random.choice(test_types),
                    test_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                    status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
                    results=f'Test results for {disease.name}' if random.choice([True, False]) else '',
                    normal_range=f'Normal range: {random.randint(10, 100)}-{random.randint(100, 200)}',
                    notes=f'Test notes for {disease.name}'
                )

        # Create treatments
        for patient in patients:
            # Each patient has 1-3 treatments
            num_treatments = random.randint(1, 3)
            patient_diseases = patient.patient_diseases.all()
            
            for i in range(num_treatments):
                if patient_diseases.exists():
                    disease = random.choice(patient_diseases).disease
                    
                    treatment = Treatment.objects.create(
                        patient=patient,
                        disease=disease,
                        treatment_name=f'Treatment for {disease.name}',
                        description=f'Treatment description for {disease.name}',
                        start_date=datetime.now().date() - timedelta(days=random.randint(1, 90)),
                        end_date=datetime.now().date() + timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                        status=random.choice(['ACTIVE', 'COMPLETED', 'CANCELLED']),
                        notes=f'Treatment notes for {disease.name}'
                    )
                    
                    # Add medicines to treatment
                    num_medicines = random.randint(1, 3)
                    treatment_medicines = random.sample(medicines, min(num_medicines, len(medicines)))
                    
                    for medicine in treatment_medicines:
                        TreatmentMedicine.objects.create(
                            treatment=treatment,
                            medicine=medicine,
                            dosage=f'{random.randint(1, 3)} tablets',
                            frequency=f'{random.randint(1, 3)} times daily',
                            duration_days=random.randint(7, 30),
                            instructions=f'Take with food'
                        )

        # Create surgeries
        surgery_names = ['Appendectomy', 'Gallbladder Removal', 'Hernia Repair', 'Knee Replacement', 'Hip Replacement', 'Cataract Surgery', 'Angioplasty', 'Bypass Surgery']
        
        for patient in patients:
            # 20% chance of having surgery
            if random.choice([True, False, False, False, False]):
                Surgery.objects.create(
                    patient=patient,
                    surgery_name=random.choice(surgery_names),
                    description=f'Surgery description for {random.choice(surgery_names)}',
                    scheduled_date=datetime.now() + timedelta(days=random.randint(1, 90)),
                    actual_date=datetime.now() + timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                    status=random.choice(['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'POSTPONED']),
                    surgeon_name=f'Dr. {random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones"])}',
                    complications=random.choice(['NONE', 'MINOR', 'MAJOR', 'CRITICAL']),
                    complications_description=f'Complications description' if random.choice([True, False]) else '',
                    notes=f'Surgery notes'
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample data!')
        )
