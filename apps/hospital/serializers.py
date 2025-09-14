from rest_framework import serializers
from .models import City, Center, Doctor, Staff, Medicine, Disease
from apps.accounts.serializers import UserSerializer


class CitySerializer(serializers.ModelSerializer):
    centers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_centers_count(self, obj):
        return obj.centers.count()


class CenterSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    doctors_count = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Center
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_doctors_count(self, obj):
        return obj.doctors.count()
    
    def get_staff_count(self, obj):
        return obj.staff.count()


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    center_name = serializers.CharField(source='center.name', read_only=True)
    city_name = serializers.CharField(source='center.city.name', read_only=True)
    patients_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_patients_count(self, obj):
        return obj.patients.count()


class DoctorCreateSerializer(serializers.ModelSerializer):
    user_data = serializers.DictField(write_only=True)
    
    class Meta:
        model = Doctor
        fields = ('center', 'specialization', 'license_number', 'experience_years', 
                 'consultation_fee', 'is_available', 'user_data')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data')
        user = User.objects.create_user(**user_data, role='DOCTOR')
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    center_name = serializers.CharField(source='center.name', read_only=True)
    city_name = serializers.CharField(source='center.city.name', read_only=True)
    
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StaffCreateSerializer(serializers.ModelSerializer):
    user_data = serializers.DictField(write_only=True)
    
    class Meta:
        model = Staff
        fields = ('center', 'department', 'employee_id', 'salary', 'is_active', 'user_data')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data')
        user = User.objects.create_user(**user_data, role='STAFF')
        staff = Staff.objects.create(user=user, **validated_data)
        return staff


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
