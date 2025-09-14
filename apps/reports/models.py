from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class Report(models.Model):
    """
    Report model to track generated reports
    """
    REPORT_TYPE_CHOICES = [
        ('PATIENT_RECORD', _('سجل المريض')),
        ('TEST_RESULTS', _('نتائج الفحوصات')),
        ('TREATMENT_SUMMARY', _('ملخص العلاج')),
        ('SURGERY_REPORT', _('تقرير الجراحة')),
        ('PATIENTS_PER_CITY', _('المرضى حسب المدينة')),
        ('COMMON_DISEASES', _('الأمراض الشائعة')),
        ('CENTER_STATISTICS', _('إحصائيات المركز')),
    ]
    
    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', _('في الانتظار')),
        ('GENERATING', _('قيد التوليد')),
        ('COMPLETED', _('مكتمل')),
        ('FAILED', _('فشل')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('اسم التقرير'))
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name=_('نوع التقرير'))
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, verbose_name=_('الصيغة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name=_('الحالة'))
    file_path = models.CharField(max_length=500, blank=True, verbose_name=_('مسار الملف'))
    parameters = models.JSONField(default=dict, blank=True, verbose_name=_('المعاملات'))  # Store report parameters
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports', verbose_name=_('تم توليده بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الإكمال'))
    
    class Meta:
        db_table = 'reports'
        verbose_name = _('تقرير')
        verbose_name_plural = _('التقارير')
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['status']),
            models.Index(fields=['generated_by']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
