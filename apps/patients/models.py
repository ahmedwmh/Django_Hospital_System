from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.hospital.models import Doctor, Disease, Medicine


class Patient(models.Model):
    """
    Patient model - belongs to Doctor, has many Diseases, Tests, Treatments, Surgeries
    """
    GENDER_CHOICES = [
        ('M', _('ذكر')),
        ('F', _('أنثى')),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_patients', verbose_name=_('المستخدم الذي أنشأ السجل'))
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients', verbose_name=_('الطبيب'))
    patient_name = models.CharField(max_length=200, default='', verbose_name=_('اسم المريض'), help_text=_('الاسم الكامل للمريض'))
    patient_id = models.CharField(
        max_length=11, 
        unique=True, 
        verbose_name=_('رقم هاتف المريض'),
        validators=[RegexValidator(
            regex=r'^\d{11}$',
            message='رقم الهاتف يجب أن يكون 11 رقماً فقط'
        )]
    )
    date_of_birth = models.DateField(verbose_name=_('تاريخ الميلاد'))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_('الجنس'))
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, verbose_name=_('فصيلة الدم'))
    address = models.TextField(verbose_name=_('العنوان'))
    emergency_contact_name = models.CharField(max_length=100, verbose_name=_('اسم جهة الاتصال في الطوارئ'))
    emergency_contact_phone = models.CharField(max_length=17, verbose_name=_('رقم هاتف جهة الاتصال في الطوارئ'))
    medical_history = models.TextField(blank=True, verbose_name=_('التاريخ الطبي'))
    allergies = models.TextField(blank=True, verbose_name=_('الحساسيات'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        db_table = 'patients'
        indexes = [
            models.Index(fields=['doctor']),
            models.Index(fields=['patient_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['date_of_birth']),
        ]
    
    def __str__(self):
        # Use patient_name if available, otherwise fall back to user name
        if self.patient_name and self.patient_name.strip():
            return f"{self.patient_name} ({self.patient_id})"
        else:
            return f"{self.user.get_full_name()} ({self.patient_id})"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class PatientDisease(models.Model):
    """
    Many-to-many relationship between Patient and Disease
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_diseases')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='patient_diseases')
    diagnosed_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('TREATED', 'Treated'),
        ('CHRONIC', 'Chronic'),
        ('CURED', 'Cured'),
    ], default='ACTIVE')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_diseases'
        unique_together = ['patient', 'disease']
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['disease']),
            models.Index(fields=['status']),
            models.Index(fields=['diagnosed_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.disease.name}"


class Test(models.Model):
    """
    Test model - belongs to Disease, belongs to Patient
    """
    TEST_TYPE_CHOICES = [
        ('BLOOD', 'Blood Test'),
        ('URINE', 'Urine Test'),
        ('XRAY', 'X-Ray'),
        ('CT', 'CT Scan'),
        ('MRI', 'MRI'),
        ('ECG', 'ECG'),
        ('ECHO', 'Echocardiogram'),
        ('ULTRASOUND', 'Ultrasound'),
        ('BIOPSY', 'Biopsy'),
        ('CULTURE', 'Culture'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tests')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='tests')
    test_name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    test_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    results = models.TextField(blank=True)
    normal_range = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tests'
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['disease']),
            models.Index(fields=['test_type']),
            models.Index(fields=['status']),
            models.Index(fields=['test_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.test_name}"


class Treatment(models.Model):
    """
    Treatment model - many-to-many with Medicines, belongs to Patient
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatments')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='treatments')
    treatment_name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'treatments'
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['disease']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.treatment_name}"


class TreatmentMedicine(models.Model):
    """
    Many-to-many relationship between Treatment and Medicine
    """
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='treatment_medicines')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='treatment_medicines')
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g., "2 times daily", "every 8 hours"
    duration_days = models.PositiveIntegerField()
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'treatment_medicines'
        unique_together = ['treatment', 'medicine']
        indexes = [
            models.Index(fields=['treatment']),
            models.Index(fields=['medicine']),
        ]
    
    def __str__(self):
        return f"{self.treatment.treatment_name} - {self.medicine.name}"


class Surgery(models.Model):
    """
    Surgery model - belongs to Patient, complications, date
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('POSTPONED', 'Postponed'),
    ]
    
    COMPLICATION_CHOICES = [
        ('NONE', 'No Complications'),
        ('MINOR', 'Minor Complications'),
        ('MAJOR', 'Major Complications'),
        ('CRITICAL', 'Critical Complications'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='surgeries')
    surgery_name = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_date = models.DateTimeField()
    actual_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    surgeon_name = models.CharField(max_length=200)
    complications = models.CharField(max_length=20, choices=COMPLICATION_CHOICES, default='NONE')
    complications_description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'surgeries'
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['surgeon_name']),
        ]
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.surgery_name}"


class Visit(models.Model):
    """
    Patient visit model - tracks when patients come to the hospital
    """
    VISIT_TYPE_CHOICES = [
        ('CONSULTATION', _('استشارة')),
        ('FOLLOW_UP', _('متابعة')),
        ('EMERGENCY', _('طوارئ')),
        ('ROUTINE', _('روتيني')),
        ('VACCINATION', _('تطعيم')),
        ('OTHER', _('أخرى')),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', _('مجدولة')),
        ('IN_PROGRESS', _('قيد التنفيذ')),
        ('COMPLETED', _('مكتملة')),
        ('CANCELLED', _('ملغية')),
        ('NO_SHOW', _('لم يحضر')),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits', verbose_name=_('المريض'))
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='visits', verbose_name=_('الطبيب'))
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='CONSULTATION', verbose_name=_('نوع الزيارة'))
    visit_date = models.DateTimeField(verbose_name=_('تاريخ ووقت الزيارة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED', verbose_name=_('حالة الزيارة'))
    chief_complaint = models.TextField(verbose_name=_('الشكوى الرئيسية'), help_text=_('وصف المشكلة أو السبب في الزيارة'))
    diagnosis = models.TextField(blank=True, verbose_name=_('التشخيص'), help_text=_('التشخيص الطبي'))
    treatment_plan = models.TextField(blank=True, verbose_name=_('خطة العلاج'), help_text=_('العلاج الموصى به'))
    notes = models.TextField(blank=True, verbose_name=_('ملاحظات إضافية'))
    follow_up_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ المتابعة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('زيارة')
        verbose_name_plural = _('الزيارات')
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['doctor']),
            models.Index(fields=['visit_date']),
            models.Index(fields=['status']),
            models.Index(fields=['visit_type']),
        ]
    
    def __str__(self):
        return f"{self.patient.patient_name or self.patient.user.get_full_name()} - {self.get_visit_type_display()} - {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
