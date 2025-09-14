from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('ADMIN', _('مدير النظام')),
        ('DOCTOR', _('طبيب')),
        ('STAFF', _('موظف')),
        ('PATIENT', _('مريض')),
    ]
    
    email = models.EmailField(unique=True, verbose_name=_('البريد الإلكتروني'))
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name=_('رقم الهاتف'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT', verbose_name=_('الدور'))
    is_verified = models.BooleanField(default=False, verbose_name=_('مُتحقق'))
    is_staff = models.BooleanField(default=False, verbose_name=_('موظف'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Arabic labels for inherited fields
        self._meta.get_field('username').verbose_name = _('اسم المستخدم')
        self._meta.get_field('first_name').verbose_name = _('الاسم الأول')
        self._meta.get_field('last_name').verbose_name = _('الاسم الأخير')
        self._meta.get_field('password').verbose_name = _('كلمة المرور')
        self._meta.get_field('is_active').verbose_name = _('نشط')
        self._meta.get_field('is_superuser').verbose_name = _('مدير عام')
    
    def save(self, *args, **kwargs):
        # Auto-generate username from email if not provided
        if not self.username and self.email:
            # Use email prefix as username, ensure uniqueness
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'
    
    @property
    def is_patient(self):
        return self.role == 'PATIENT'
