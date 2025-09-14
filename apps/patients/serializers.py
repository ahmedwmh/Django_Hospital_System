from rest_framework import serializers
from .models import Patient, PatientDisease, Test, Treatment, TreatmentMedicine, Surgery
from apps.hospital.serializers import DoctorSerializer, DiseaseSerializer, MedicineSerializer
from apps.accounts.serializers import UserSerializer
from apps.accounts.models import User


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    center_name = serializers.CharField(source='doctor.center.name', read_only=True)
    city_name = serializers.CharField(source='doctor.center.city.name', read_only=True)
    age = serializers.ReadOnlyField()
    diseases_count = serializers.SerializerMethodField()
    tests_count = serializers.SerializerMethodField()
    treatments_count = serializers.SerializerMethodField()
    surgeries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'patient_id')
    
    def get_diseases_count(self, obj):
        return obj.patient_diseases.count()
    
    def get_tests_count(self, obj):
        return obj.tests.count()
    
    def get_treatments_count(self, obj):
        return obj.treatments.count()
    
    def get_surgeries_count(self, obj):
        return obj.surgeries.count()


class PatientCreateSerializer(serializers.ModelSerializer):
    user_data = serializers.DictField(write_only=True)
    
    class Meta:
        model = Patient
        fields = ('doctor', 'date_of_birth', 'gender', 'blood_group', 'address',
                 'emergency_contact_name', 'emergency_contact_phone', 'medical_history',
                 'allergies', 'is_active', 'user_data')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data')
        user = User.objects.create_user(**user_data, role='PATIENT')
        
        # Generate patient ID
        import uuid
        patient_id = f"PAT{str(uuid.uuid4())[:8].upper()}"
        
        patient = Patient.objects.create(
            user=user, 
            patient_id=patient_id,
            **validated_data
        )
        return patient


class PatientDiseaseSerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source='disease.name', read_only=True)
    disease_category = serializers.CharField(source='disease.category', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    
    class Meta:
        model = PatientDisease
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TestSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    disease_name = serializers.CharField(source='disease.name', read_only=True)
    doctor_name = serializers.CharField(source='patient.doctor.user.get_full_name', read_only=True)
    
    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TreatmentMedicineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_strength = serializers.CharField(source='medicine.strength', read_only=True)
    
    class Meta:
        model = TreatmentMedicine
        fields = '__all__'
        read_only_fields = ('created_at',)


class TreatmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    disease_name = serializers.CharField(source='disease.name', read_only=True)
    doctor_name = serializers.CharField(source='patient.doctor.user.get_full_name', read_only=True)
    medicines = TreatmentMedicineSerializer(source='treatment_medicines', many=True, read_only=True)
    
    class Meta:
        model = Treatment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class SurgerySerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    doctor_name = serializers.CharField(source='patient.doctor.user.get_full_name', read_only=True)
    
    class Meta:
        model = Surgery
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PatientSummarySerializer(serializers.ModelSerializer):
    """
    Optimized serializer for mobile app - includes only essential fields
    """
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone_number', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    center_name = serializers.CharField(source='doctor.center.name', read_only=True)
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = ('id', 'patient_id', 'name', 'email', 'phone', 'date_of_birth', 
                 'gender', 'blood_group', 'doctor_name', 'center_name', 'age', 
                 'is_active', 'created_at')
