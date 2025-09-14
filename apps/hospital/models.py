from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class City(models.Model):
    """
    City model - has many Centers
    """
    IRAQ_CITIES = [
        ('BAGHDAD', _('بغداد')),
        ('BASRA', _('البصرة')),
        ('MOSUL', _('الموصل')),
        ('ERBIL', _('أربيل')),
        ('NAJAF', _('النجف')),
        ('KARBALA', _('كربلاء')),
        ('KIRKUK', _('كركوك')),
        ('NAJAF', _('النجف')),
        ('SULAYMANIYAH', _('السليمانية')),
        ('WASIT', _('واسط')),
        ('BABIL', _('بابل')),
        ('QADISIYAH', _('القادسية')),
        ('MAYSAN', _('ميسان')),
        ('DIWANIYAH', _('الديوانية')),
        ('MUTHANNA', _('المثنى')),
        ('THI_QAR', _('ذي قار')),
        ('ANBAR', _('الأنبار')),
        ('SALAH_AL_DIN', _('صلاح الدين')),
        ('DIYALA', _('ديالى')),
        ('DUHOK', _('دهوك')),
    ]
    
    name = models.CharField(max_length=100, choices=IRAQ_CITIES, unique=True, verbose_name=_('اسم المدينة'))
    state = models.CharField(max_length=100, verbose_name=_('المحافظة'))
    country = models.CharField(max_length=100, default='Iraq', verbose_name=_('البلد'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        db_table = 'cities'
        verbose_name = _('مدينة')
        verbose_name_plural = _('المدن')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['state']),
        ]
    
    def __str__(self):
        return f"{self.get_name_display()}, {self.state}"


class Center(models.Model):
    """
    Center model - belongs to City, has Doctors and Staff
    """
    name = models.CharField(max_length=200, verbose_name=_('اسم المركز'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='centers', verbose_name=_('المدينة'))
    address = models.TextField(verbose_name=_('العنوان'))
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, verbose_name=_('رقم الهاتف'))
    email = models.EmailField(blank=True, verbose_name=_('البريد الإلكتروني'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        db_table = 'centers'
        verbose_name = _('مركز طبي')
        verbose_name_plural = _('المراكز الطبية')
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city.get_name_display()}"


class Doctor(models.Model):
    """
    Doctor model - belongs to Center, manages Patients
    """
    SPECIALIZATION_CHOICES = [
        ('CARDIOLOGY', _('أمراض القلب')),
        ('NEUROLOGY', _('أمراض الأعصاب')),
        ('ONCOLOGY', _('الأورام')),
        ('PEDIATRICS', _('طب الأطفال')),
        ('GYNECOLOGY', _('أمراض النساء والولادة')),
        ('ORTHOPEDICS', _('العظام')),
        ('DERMATOLOGY', _('الأمراض الجلدية')),
        ('PSYCHIATRY', _('الطب النفسي')),
        ('RADIOLOGY', _('الأشعة')),
        ('ANESTHESIOLOGY', _('التخدير')),
        ('EMERGENCY', _('الطوارئ')),
        ('GENERAL', _('الطب العام')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', verbose_name=_('المستخدم'))
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='doctors', verbose_name=_('المركز'))
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES, verbose_name=_('التخصص'))
    license_number = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name=_('رقم الترخيص'))
    experience_years = models.PositiveIntegerField(default=0, verbose_name=_('سنوات الخبرة'))
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('رسوم الاستشارة'))
    is_available = models.BooleanField(default=True, verbose_name=_('متاح'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        db_table = 'doctors'
        verbose_name = _('طبيب')
        verbose_name_plural = _('الأطباء')
        indexes = [
            models.Index(fields=['center']),
            models.Index(fields=['specialization']),
            models.Index(fields=['is_available']),
            models.Index(fields=['license_number']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.get_specialization_display()}"


class Staff(models.Model):
    """
    Staff model - belongs to Center, limited permissions
    """
    DEPARTMENT_CHOICES = [
        ('ADMINISTRATION', 'Administration'),
        ('NURSING', 'Nursing'),
        ('LABORATORY', 'Laboratory'),
        ('PHARMACY', 'Pharmacy'),
        ('RADIOLOGY', 'Radiology'),
        ('RECEPTION', 'Reception'),
        ('HOUSEKEEPING', 'Housekeeping'),
        ('SECURITY', 'Security'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='staff')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    employee_id = models.CharField(max_length=50, unique=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff'
        indexes = [
            models.Index(fields=['center']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
            models.Index(fields=['employee_id']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_department_display()}"


class Medicine(models.Model):
    """
    Medicine model - name, dosage, side effects
    """
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    dosage_form = models.CharField(max_length=50)  # tablet, syrup, injection, etc.
    strength = models.CharField(max_length=100)  # 500mg, 10ml, etc.
    manufacturer = models.CharField(max_length=200)
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    is_prescription_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medicines'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['generic_name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.strength})"


class Disease(models.Model):
    """
    Disease model - many-to-many with Patient, has many Tests
    """
    CATEGORY_CHOICES = [
        ('INFECTIOUS', 'Infectious'),
        ('CHRONIC', 'Chronic'),
        ('ACUTE', 'Acute'),
        ('GENETIC', 'Genetic'),
        ('MENTAL', 'Mental Health'),
        ('CARDIOVASCULAR', 'Cardiovascular'),
        ('RESPIRATORY', 'Respiratory'),
        ('NEUROLOGICAL', 'Neurological'),
        ('CANCER', 'Cancer'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    icd_code = models.CharField(max_length=20, blank=True)  # International Classification of Diseases
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'diseases'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['icd_code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
