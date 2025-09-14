from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .serializers import DashboardStatsSerializer
from apps.hospital.models import City, Center, Doctor, Staff, Disease, Medicine
from apps.patients.models import Patient, Test, Treatment, Surgery
from apps.accounts.models import User
from apps.hospital.permissions import IsAdminOrReadOnly


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard statistics and analytics
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get overview statistics"""
        stats = {
            'total_users': User.objects.count(),
            'total_patients': Patient.objects.count(),
            'total_doctors': Doctor.objects.count(),
            'total_staff': Staff.objects.count(),
            'total_centers': Center.objects.count(),
            'total_cities': City.objects.count(),
            'total_diseases': Disease.objects.count(),
            'total_medicines': Medicine.objects.count(),
            'active_patients': Patient.objects.filter(is_active=True).count(),
            'available_doctors': Doctor.objects.filter(is_available=True).count(),
            'active_staff': Staff.objects.filter(is_active=True).count(),
            'active_centers': Center.objects.filter(is_active=True).count(),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def patients_by_city(self, request):
        """Get patient count per city"""
        cities = City.objects.annotate(
            patients_count=Count('centers__doctors__patients')
        ).order_by('-patients_count')
        
        data = []
        for city in cities:
            data.append({
                'city_name': city.name,
                'state': city.state,
                'patients_count': city.patients_count,
                'centers_count': city.centers.count(),
                'doctors_count': sum(center.doctors.count() for center in city.centers.all())
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def patients_by_center(self, request):
        """Get patient count per center"""
        centers = Center.objects.annotate(
            patients_count=Count('doctors__patients')
        ).order_by('-patients_count')
        
        data = []
        for center in centers:
            data.append({
                'center_name': center.name,
                'city_name': center.city.name,
                'patients_count': center.patients_count,
                'doctors_count': center.doctors.count(),
                'staff_count': center.staff.count(),
                'is_active': center.is_active
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def common_diseases(self, request):
        """Get most common diseases"""
        limit = request.query_params.get('limit', 10)
        diseases = Disease.objects.annotate(
            patient_count=Count('patient_diseases')
        ).filter(patient_count__gt=0).order_by('-patient_count')[:int(limit)]
        
        data = []
        for disease in diseases:
            data.append({
                'disease_name': disease.name,
                'category': disease.get_category_display(),
                'patient_count': disease.patient_count,
                'icd_code': disease.icd_code
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def upcoming_surgeries(self, request):
        """Get upcoming surgeries"""
        limit = request.query_params.get('limit', 10)
        upcoming_surgeries = Surgery.objects.filter(
            status='SCHEDULED',
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')[:int(limit)]
        
        data = []
        for surgery in upcoming_surgeries:
            data.append({
                'surgery_name': surgery.surgery_name,
                'patient_name': surgery.patient.user.get_full_name(),
                'patient_id': surgery.patient.patient_id,
                'surgeon_name': surgery.surgeon_name,
                'scheduled_date': surgery.scheduled_date,
                'center_name': surgery.patient.doctor.center.name,
                'city_name': surgery.patient.doctor.center.city.name
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def recent_tests(self, request):
        """Get recent tests"""
        limit = request.query_params.get('limit', 20)
        recent_tests = Test.objects.select_related(
            'patient__user', 'disease', 'patient__doctor__user'
        ).order_by('-test_date')[:int(limit)]
        
        data = []
        for test in recent_tests:
            data.append({
                'test_name': test.test_name,
                'test_type': test.get_test_type_display(),
                'patient_name': test.patient.user.get_full_name(),
                'patient_id': test.patient.patient_id,
                'disease_name': test.disease.name,
                'test_date': test.test_date,
                'status': test.get_status_display(),
                'doctor_name': test.patient.doctor.user.get_full_name()
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def active_treatments(self, request):
        """Get active treatments"""
        limit = request.query_params.get('limit', 20)
        active_treatments = Treatment.objects.filter(
            status='ACTIVE'
        ).select_related(
            'patient__user', 'disease', 'patient__doctor__user'
        ).order_by('-start_date')[:int(limit)]
        
        data = []
        for treatment in active_treatments:
            data.append({
                'treatment_name': treatment.treatment_name,
                'patient_name': treatment.patient.user.get_full_name(),
                'patient_id': treatment.patient.patient_id,
                'disease_name': treatment.disease.name,
                'start_date': treatment.start_date,
                'end_date': treatment.end_date,
                'doctor_name': treatment.patient.doctor.user.get_full_name(),
                'medicines_count': treatment.treatment_medicines.count()
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def monthly_statistics(self, request):
        """Get monthly statistics for the last 12 months"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        # Get monthly data
        months = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            next_month = current_date + timedelta(days=32)
            next_month = next_month.replace(day=1)
            
            month_start = current_date
            month_end = next_month - timedelta(days=1)
            
            # Count new patients in this month
            new_patients = Patient.objects.filter(
                created_at__range=[month_start, month_end]
            ).count()
            
            # Count new tests in this month
            new_tests = Test.objects.filter(
                test_date__range=[month_start, month_end]
            ).count()
            
            # Count new treatments in this month
            new_treatments = Treatment.objects.filter(
                start_date__range=[month_start, month_end]
            ).count()
            
            # Count new surgeries in this month
            new_surgeries = Surgery.objects.filter(
                scheduled_date__range=[month_start, month_end]
            ).count()
            
            months.append({
                'month': current_date.strftime('%Y-%m'),
                'month_name': current_date.strftime('%B %Y'),
                'new_patients': new_patients,
                'new_tests': new_tests,
                'new_treatments': new_treatments,
                'new_surgeries': new_surgeries
            })
            
            current_date = next_month
        
        return Response(months)
    
    @action(detail=False, methods=['get'])
    def doctor_statistics(self, request):
        """Get doctor statistics"""
        doctors = Doctor.objects.select_related('user', 'center__city').annotate(
            patients_count=Count('patients'),
            tests_count=Count('patients__tests'),
            treatments_count=Count('patients__treatments'),
            surgeries_count=Count('patients__surgeries')
        ).order_by('-patients_count')
        
        data = []
        for doctor in doctors:
            data.append({
                'doctor_name': doctor.user.get_full_name(),
                'specialization': doctor.get_specialization_display(),
                'center_name': doctor.center.name,
                'city_name': doctor.center.city.name,
                'experience_years': doctor.experience_years,
                'consultation_fee': float(doctor.consultation_fee),
                'is_available': doctor.is_available,
                'patients_count': doctor.patients_count,
                'tests_count': doctor.tests_count,
                'treatments_count': doctor.treatments_count,
                'surgeries_count': doctor.surgeries_count
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def test_statistics(self, request):
        """Get test statistics"""
        test_types = Test.objects.values('test_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        test_statuses = Test.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        recent_tests = Test.objects.filter(
            test_date__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        data = {
            'total_tests': Test.objects.count(),
            'recent_tests': recent_tests,
            'by_type': list(test_types),
            'by_status': list(test_statuses)
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def surgery_statistics(self, request):
        """Get surgery statistics"""
        surgery_statuses = Surgery.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        surgery_complications = Surgery.objects.values('complications').annotate(
            count=Count('id')
        ).order_by('-count')
        
        upcoming_surgeries = Surgery.objects.filter(
            status='SCHEDULED',
            scheduled_date__gte=timezone.now()
        ).count()
        
        data = {
            'total_surgeries': Surgery.objects.count(),
            'upcoming_surgeries': upcoming_surgeries,
            'by_status': list(surgery_statuses),
            'by_complications': list(surgery_complications)
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def mobile_dashboard(self, request):
        """Get mobile-optimized dashboard data"""
        user = request.user
        
        if user.is_admin:
            # Admin dashboard
            stats = {
                'total_patients': Patient.objects.count(),
                'total_doctors': Doctor.objects.count(),
                'total_centers': Center.objects.count(),
                'active_patients': Patient.objects.filter(is_active=True).count(),
                'available_doctors': Doctor.objects.filter(is_available=True).count(),
                'upcoming_surgeries': Surgery.objects.filter(
                    status='SCHEDULED',
                    scheduled_date__gte=timezone.now()
                ).count(),
                'pending_tests': Test.objects.filter(status='PENDING').count(),
                'active_treatments': Treatment.objects.filter(status='ACTIVE').count(),
            }
        elif user.is_doctor:
            # Doctor dashboard
            doctor = user.doctor_profile
            stats = {
                'my_patients': doctor.patients.count(),
                'active_patients': doctor.patients.filter(is_active=True).count(),
                'pending_tests': Test.objects.filter(
                    patient__doctor=doctor,
                    status='PENDING'
                ).count(),
                'active_treatments': Treatment.objects.filter(
                    patient__doctor=doctor,
                    status='ACTIVE'
                ).count(),
                'upcoming_surgeries': Surgery.objects.filter(
                    patient__doctor=doctor,
                    status='SCHEDULED',
                    scheduled_date__gte=timezone.now()
                ).count(),
            }
        elif user.is_patient:
            # Patient dashboard
            patient = user.patient_profile
            stats = {
                'my_tests': patient.tests.count(),
                'pending_tests': patient.tests.filter(status='PENDING').count(),
                'completed_tests': patient.tests.filter(status='COMPLETED').count(),
                'active_treatments': patient.treatments.filter(status='ACTIVE').count(),
                'upcoming_surgeries': patient.surgeries.filter(
                    status='SCHEDULED',
                    scheduled_date__gte=timezone.now()
                ).count(),
                'diseases': patient.patient_diseases.count(),
            }
        else:
            stats = {}
        
        return Response(stats)
