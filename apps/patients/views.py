from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import DetailView
from django.urls import reverse
from django.utils.html import format_html
from .models import Patient, PatientDisease, Test, Treatment, TreatmentMedicine, Surgery
from .serializers import (
    PatientSerializer, PatientCreateSerializer, PatientSummarySerializer,
    PatientDiseaseSerializer, TestSerializer, TreatmentSerializer,
    TreatmentMedicineSerializer, SurgerySerializer
)
from apps.hospital.permissions import IsOwnerOrDoctorOrAdmin, IsPatientOrDoctorOrAdmin
from apps.hospital.models import City, Center, Doctor


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patients
    """
    queryset = Patient.objects.select_related(
        'user', 'doctor__user', 'doctor__center__city'
    ).prefetch_related('patient_diseases__disease', 'tests', 'treatments', 'surgeries')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'patient_id']
    filterset_fields = ['doctor', 'gender', 'blood_group', 'is_active']
    ordering_fields = ['user__first_name', 'created_at', 'date_of_birth']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PatientCreateSerializer
        elif self.action == 'list' and self.request.query_params.get('mobile') == 'true':
            return PatientSummarySerializer
        return PatientSerializer
    
    def get_queryset(self):
        """
        Filter patients based on user role
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        elif user.is_doctor:
            return self.queryset.filter(doctor__user=user)
        elif user.is_patient:
            return self.queryset.filter(user=user)
        else:
            return self.queryset.none()
    
    @action(detail=True, methods=['get'])
    def diseases(self, request, pk=None):
        """Get all diseases of a patient"""
        patient = self.get_object()
        diseases = patient.patient_diseases.select_related('disease')
        serializer = PatientDiseaseSerializer(diseases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tests(self, request, pk=None):
        """Get all tests of a patient"""
        patient = self.get_object()
        tests = patient.tests.select_related('disease')
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def treatments(self, request, pk=None):
        """Get all treatments of a patient"""
        patient = self.get_object()
        treatments = patient.treatments.select_related('disease').prefetch_related('treatment_medicines__medicine')
        serializer = TreatmentSerializer(treatments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def surgeries(self, request, pk=None):
        """Get all surgeries of a patient"""
        patient = self.get_object()
        surgeries = patient.surgeries.all()
        serializer = SurgerySerializer(surgeries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_doctor(self, request):
        """Get patients by doctor"""
        doctor_id = request.query_params.get('doctor_id')
        if doctor_id:
            patients = self.queryset.filter(doctor_id=doctor_id)
        else:
            patients = self.queryset.none()
        
        serializer = self.get_serializer(patients, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get patient statistics"""
        stats = {
            'total_patients': Patient.objects.count(),
            'active_patients': Patient.objects.filter(is_active=True).count(),
            'by_gender': Patient.objects.values('gender').annotate(
                count=Count('id')
            ).order_by('-count'),
            'by_blood_group': Patient.objects.values('blood_group').annotate(
                count=Count('id')
            ).order_by('-count'),
            'by_doctor': Patient.objects.values('doctor__user__first_name', 'doctor__user__last_name').annotate(
                count=Count('id')
            ).order_by('-count'),
        }
        return Response(stats)


class PatientDiseaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patient diseases
    """
    queryset = PatientDisease.objects.select_related('patient__user', 'disease')
    serializer_class = PatientDiseaseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'disease__name']
    filterset_fields = ['patient', 'disease', 'status']
    ordering_fields = ['diagnosed_date', 'created_at']
    ordering = ['-diagnosed_date']
    
    def get_queryset(self):
        """
        Filter patient diseases based on user role
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        elif user.is_doctor:
            return self.queryset.filter(patient__doctor__user=user)
        elif user.is_patient:
            return self.queryset.filter(patient__user=user)
        else:
            return self.queryset.none()


class TestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tests
    """
    queryset = Test.objects.select_related('patient__user', 'disease', 'patient__doctor__user')
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'test_name', 'disease__name']
    filterset_fields = ['patient', 'disease', 'test_type', 'status']
    ordering_fields = ['test_date', 'created_at']
    ordering = ['-test_date']
    
    def get_queryset(self):
        """
        Filter tests based on user role
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        elif user.is_doctor:
            return self.queryset.filter(patient__doctor__user=user)
        elif user.is_patient:
            return self.queryset.filter(patient__user=user)
        else:
            return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get tests grouped by type"""
        test_type = request.query_params.get('test_type')
        if test_type:
            tests = self.queryset.filter(test_type=test_type)
        else:
            tests = self.queryset.all()
        
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending tests"""
        tests = self.queryset.filter(status='PENDING')
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)


class TreatmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing treatments
    """
    queryset = Treatment.objects.select_related('patient__user', 'disease', 'patient__doctor__user').prefetch_related('treatment_medicines__medicine')
    serializer_class = TreatmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'treatment_name', 'disease__name']
    filterset_fields = ['patient', 'disease', 'status']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """
        Filter treatments based on user role
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        elif user.is_doctor:
            return self.queryset.filter(patient__doctor__user=user)
        elif user.is_patient:
            return self.queryset.filter(patient__user=user)
        else:
            return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active treatments"""
        treatments = self.queryset.filter(status='ACTIVE')
        serializer = TreatmentSerializer(treatments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_medicine(self, request, pk=None):
        """Add medicine to treatment"""
        treatment = self.get_object()
        medicine_data = request.data
        medicine_data['treatment'] = treatment.id
        
        serializer = TreatmentMedicineSerializer(data=medicine_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurgeryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing surgeries
    """
    queryset = Surgery.objects.select_related('patient__user', 'patient__doctor__user')
    serializer_class = SurgerySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'surgery_name', 'surgeon_name']
    filterset_fields = ['patient', 'status', 'complications']
    ordering_fields = ['scheduled_date', 'created_at']
    ordering = ['-scheduled_date']
    
    def get_queryset(self):
        """
        Filter surgeries based on user role
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        elif user.is_doctor:
            return self.queryset.filter(patient__doctor__user=user)
        elif user.is_patient:
            return self.queryset.filter(patient__user=user)
        else:
            return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming surgeries"""
        from django.utils import timezone
        surgeries = self.queryset.filter(
            status='SCHEDULED',
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')
        
        serializer = SurgerySerializer(surgeries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get surgeries by status"""
        status = request.query_params.get('status')
        if status:
            surgeries = self.queryset.filter(status=status)
        else:
            surgeries = self.queryset.all()
        
        serializer = SurgerySerializer(surgeries, many=True)
        return Response(serializer.data)


# AJAX endpoints for admin form filtering
@csrf_exempt
@require_http_methods(["GET"])
def get_centers_by_city(request):
    """Get centers filtered by city"""
    city_id = request.GET.get('city_id')
    if city_id:
        centers = Center.objects.filter(city_id=city_id).values('id', 'name')
        return JsonResponse({'centers': list(centers)})
    return JsonResponse({'centers': []})


@csrf_exempt
@require_http_methods(["GET"])
def get_doctors_by_center(request):
    """Get doctors filtered by center"""
    center_id = request.GET.get('center_id')
    if center_id and center_id != 'any':
        doctors = Doctor.objects.filter(center_id=center_id).select_related('user').values(
            'id', 'user__first_name', 'user__last_name', 'specialization'
        )
    else:
        # If no center specified or 'any', return all doctors
        doctors = Doctor.objects.select_related('user').values(
            'id', 'user__first_name', 'user__last_name', 'specialization'
        )
    
    doctor_list = []
    for doctor in doctors:
        doctor_list.append({
            'id': doctor['id'],
            'name': f"{doctor['user__first_name']} {doctor['user__last_name']}",
            'specialization': doctor['specialization'] or 'غير محدد'
        })
    
    return JsonResponse({'doctors': doctor_list})


@csrf_exempt
@require_http_methods(["GET"])
def check_phone_uniqueness(request):
    """Check if phone number is unique"""
    phone = request.GET.get('phone')
    if phone:
        # Clean the phone number (remove non-digits)
        phone = ''.join(filter(str.isdigit, phone))
        
        # Check if phone exists
        exists = Patient.objects.filter(patient_id=phone).exists()
        
        return JsonResponse({
            'exists': exists,
            'phone': phone,
            'message': 'رقم الهاتف مستخدم بالفعل' if exists else 'رقم الهاتف متاح'
        })
    
    return JsonResponse({'exists': False, 'message': 'رقم الهاتف غير صحيح'})


@staff_member_required
def patient_profile(request, patient_id):
    """
    Comprehensive patient profile page with all information and quick actions
    """
    patient = get_object_or_404(
        Patient.objects.select_related(
            'user', 'doctor__user', 'doctor__center__city'
        ).prefetch_related(
            'patient_diseases__disease',
            'tests__disease',
            'treatments__disease',
            'treatments__treatment_medicines__medicine',
            'surgeries'
        ),
        id=patient_id
    )
    
    # Get all related data
    diseases = patient.patient_diseases.select_related('disease').order_by('-diagnosed_date')
    tests = patient.tests.select_related('disease').order_by('-test_date')
    treatments = patient.treatments.select_related('disease').prefetch_related('treatment_medicines__medicine').order_by('-start_date')
    surgeries = patient.surgeries.order_by('-scheduled_date')
    visits = patient.visits.select_related('doctor', 'doctor__user').order_by('-visit_date')
    
    # Statistics
    stats = {
        'total_diseases': diseases.count(),
        'active_diseases': diseases.filter(status='ACTIVE').count(),
        'total_tests': tests.count(),
        'pending_tests': tests.filter(status='PENDING').count(),
        'completed_tests': tests.filter(status='COMPLETED').count(),
        'total_treatments': treatments.count(),
        'active_treatments': treatments.filter(status='ACTIVE').count(),
        'total_surgeries': surgeries.count(),
        'upcoming_surgeries': surgeries.filter(status='SCHEDULED').count(),
        'total_visits': visits.count(),
        'completed_visits': visits.filter(status='COMPLETED').count(),
        'scheduled_visits': visits.filter(status='SCHEDULED').count(),
    }
    
    # Quick action URLs
    quick_actions = {
        'add_disease': reverse('admin:patients_patientdisease_add') + f'?patient={patient.id}',
        'add_test': reverse('admin:patients_test_add') + f'?patient={patient.id}',
        'add_treatment': reverse('admin:patients_treatment_add') + f'?patient={patient.id}',
        'add_surgery': reverse('admin:patients_surgery_add') + f'?patient={patient.id}',
        'add_visit': reverse('admin:patients_visit_add') + f'?patient={patient.id}',
        'edit_patient': reverse('admin:patients_patient_change', args=[patient.id]),
    }
    
    context = {
        'patient': patient,
        'diseases': diseases,
        'tests': tests,
        'treatments': treatments,
        'surgeries': surgeries,
        'visits': visits,
        'stats': stats,
        'quick_actions': quick_actions,
        'title': f'ملف المريض - {patient.user.get_full_name()}',
        'has_permission': True,
        'opts': Patient._meta,
    }
    
    return render(request, 'admin/patients/patient_profile.html', context)
