from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import City, Center, Doctor, Staff, Medicine, Disease
from .serializers import (
    CitySerializer, CenterSerializer, DoctorSerializer, DoctorCreateSerializer,
    StaffSerializer, StaffCreateSerializer, MedicineSerializer, DiseaseSerializer
)
from .permissions import IsAdminOrReadOnly, IsDoctorOrAdmin, IsStaffOrAdmin


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cities
    """
    queryset = City.objects.all().prefetch_related('centers')
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'state', 'country']
    filterset_fields = ['state', 'country']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def centers(self, request, pk=None):
        """Get all centers in a city"""
        city = self.get_object()
        centers = city.centers.filter(is_active=True)
        serializer = CenterSerializer(centers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get city statistics"""
        cities = City.objects.annotate(
            centers_count=Count('centers'),
            doctors_count=Count('centers__doctors'),
            staff_count=Count('centers__staff')
        ).order_by('-centers_count')
        
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def centers_by_city(self, request):
        """Get centers filtered by city"""
        city_id = request.query_params.get('city_id')
        if city_id:
            centers = Center.objects.filter(city_id=city_id, is_active=True)
            serializer = CenterSerializer(centers, many=True)
            return Response({'centers': serializer.data})
        return Response({'centers': []})


class CenterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing centers
    """
    queryset = Center.objects.select_related('city').prefetch_related('doctors', 'staff')
    serializer_class = CenterSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'city__name']
    filterset_fields = ['city', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def doctors(self, request, pk=None):
        """Get all doctors in a center"""
        center = self.get_object()
        doctors = center.doctors.filter(is_available=True)
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def staff(self, request, pk=None):
        """Get all staff in a center"""
        center = self.get_object()
        staff = center.staff.filter(is_active=True)
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get center statistics"""
        center = self.get_object()
        stats = {
            'doctors_count': center.doctors.count(),
            'staff_count': center.staff.count(),
            'patients_count': sum(doctor.patients.count() for doctor in center.doctors.all()),
            'active_doctors': center.doctors.filter(is_available=True).count(),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def doctors_by_center(self, request):
        """Get doctors filtered by center"""
        center_id = request.query_params.get('center_id')
        if center_id:
            doctors = Doctor.objects.filter(center_id=center_id, is_available=True).select_related('user')
            serializer = DoctorSerializer(doctors, many=True)
            return Response({'doctors': serializer.data})
        return Response({'doctors': []})


class DoctorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctors
    """
    queryset = Doctor.objects.select_related('user', 'center__city').prefetch_related('patients')
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'specialization']
    filterset_fields = ['center', 'specialization', 'is_available']
    ordering_fields = ['user__first_name', 'experience_years', 'created_at']
    ordering = ['user__first_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DoctorCreateSerializer
        return DoctorSerializer
    
    @action(detail=True, methods=['get'])
    def patients(self, request, pk=None):
        """Get all patients of a doctor"""
        doctor = self.get_object()
        patients = doctor.patients.filter(is_active=True)
        serializer = DoctorSerializer(patients, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_specialization(self, request):
        """Get doctors grouped by specialization"""
        specialization = request.query_params.get('specialization')
        if specialization:
            doctors = self.queryset.filter(specialization=specialization)
        else:
            doctors = self.queryset.all()
        
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get doctor statistics"""
        stats = {
            'total_doctors': Doctor.objects.count(),
            'available_doctors': Doctor.objects.filter(is_available=True).count(),
            'by_specialization': Doctor.objects.values('specialization').annotate(
                count=Count('id')
            ).order_by('-count'),
            'by_center': Doctor.objects.values('center__name').annotate(
                count=Count('id')
            ).order_by('-count'),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def doctor_info(self, request):
        """Get doctor information by ID"""
        doctor_id = request.query_params.get('doctor_id')
        if doctor_id:
            try:
                doctor = Doctor.objects.select_related('user', 'center').get(id=doctor_id)
                serializer = DoctorSerializer(doctor)
                return Response(serializer.data)
            except Doctor.DoesNotExist:
                return Response({'error': 'Doctor not found'}, status=404)
        return Response({'error': 'doctor_id parameter required'}, status=400)


class StaffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing staff
    """
    queryset = Staff.objects.select_related('user', 'center__city')
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'department']
    filterset_fields = ['center', 'department', 'is_active']
    ordering_fields = ['user__first_name', 'created_at']
    ordering = ['user__first_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StaffCreateSerializer
        return StaffSerializer
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get staff grouped by department"""
        department = request.query_params.get('department')
        if department:
            staff = self.queryset.filter(department=department)
        else:
            staff = self.queryset.all()
        
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get staff statistics"""
        stats = {
            'total_staff': Staff.objects.count(),
            'active_staff': Staff.objects.filter(is_active=True).count(),
            'by_department': Staff.objects.values('department').annotate(
                count=Count('id')
            ).order_by('-count'),
            'by_center': Staff.objects.values('center__name').annotate(
                count=Count('id')
            ).order_by('-count'),
        }
        return Response(stats)


class MedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing medicines
    """
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'generic_name', 'manufacturer']
    filterset_fields = ['dosage_form', 'is_prescription_required', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def by_dosage_form(self, request):
        """Get medicines grouped by dosage form"""
        dosage_form = request.query_params.get('dosage_form')
        if dosage_form:
            medicines = self.queryset.filter(dosage_form=dosage_form)
        else:
            medicines = self.queryset.all()
        
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search medicines by name or generic name"""
        query = request.query_params.get('q', '')
        if query:
            medicines = self.queryset.filter(
                Q(name__icontains=query) | Q(generic_name__icontains=query)
            )
        else:
            medicines = self.queryset.none()
        
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)


class DiseaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing diseases
    """
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'symptoms', 'icd_code']
    filterset_fields = ['category', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get diseases grouped by category"""
        category = request.query_params.get('category')
        if category:
            diseases = self.queryset.filter(category=category)
        else:
            diseases = self.queryset.all()
        
        serializer = DiseaseSerializer(diseases, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search diseases by name, symptoms, or ICD code"""
        query = request.query_params.get('q', '')
        if query:
            diseases = self.queryset.filter(
                Q(name__icontains=query) | 
                Q(symptoms__icontains=query) | 
                Q(icd_code__icontains=query)
            )
        else:
            diseases = self.queryset.none()
        
        serializer = DiseaseSerializer(diseases, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get disease statistics"""
        stats = {
            'total_diseases': Disease.objects.count(),
            'active_diseases': Disease.objects.filter(is_active=True).count(),
            'by_category': Disease.objects.values('category').annotate(
                count=Count('id')
            ).order_by('-count'),
        }
        return Response(stats)


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET"])
def centers_by_city(request):
    """Get centers filtered by city for admin forms"""
    city_id = request.GET.get('city_id')
    
    if not city_id:
        return JsonResponse({'centers': []})
    
    try:
        centers = Center.objects.filter(city_id=city_id).select_related('city')
        centers_data = []
        
        for center in centers:
            centers_data.append({
                'id': center.id,
                'name': center.name,
                'city_name': center.city.get_name_display(),
                'address': center.address,
                'phone_number': center.phone_number
            })
        
        return JsonResponse({'centers': centers_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
