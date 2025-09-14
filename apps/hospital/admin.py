from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.urls import reverse
from .models import City, Center, Doctor, Staff, Medicine, Disease


class CityForm(forms.ModelForm):
    """Custom form for City with enhanced functionality"""
    
    class Meta:
        model = City
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم المدينة'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم المحافظة'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم البلد'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set Arabic labels
        self.fields['name'].label = _('اسم المدينة')
        self.fields['state'].label = _('المحافظة')
        self.fields['country'].label = _('البلد')
        
        # Set help texts
        self.fields['name'].help_text = _('أدخل اسم المدينة')
        self.fields['state'].help_text = _('أدخل اسم المحافظة')
        self.fields['country'].help_text = _('أدخل اسم البلد')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityForm
    list_display = ('get_city_name', 'state', 'country', 'centers_count', 'created_at')
    list_filter = ('state', 'country', 'created_at')
    search_fields = ('name', 'state', 'country')
    ordering = ('name',)
    list_per_page = 25
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    def get_city_name(self, obj):
        """Display city name with styling"""
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            obj.name
        )
    get_city_name.short_description = _('اسم المدينة')
    
    def centers_count(self, obj):
        count = obj.centers.count()
        return format_html(
            '<span style="color: #059669; font-weight: 600;">{}</span>',
            count
        )
    centers_count.short_description = _('عدد المراكز')
    
    class Meta:
        verbose_name = _('المدينة')
        verbose_name_plural = _('المدن')


class CenterListFilter(admin.SimpleListFilter):
    title = _('حالة المركز')
    parameter_name = 'center_status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('نشط')),
            ('inactive', _('غير نشط')),
            ('with_doctors', _('يحتوي على أطباء')),
            ('without_doctors', _('بدون أطباء')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)
        if self.value() == 'with_doctors':
            return queryset.filter(doctors__isnull=False).distinct()
        if self.value() == 'without_doctors':
            return queryset.filter(doctors__isnull=True)


class CenterForm(forms.ModelForm):
    """Custom form for Center with enhanced functionality"""
    
    class Meta:
        model = Center
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم المركز'
            }),
            'city': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل عنوان المركز'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل رقم الهاتف'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل البريد الإلكتروني'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set Arabic labels
        self.fields['name'].label = _('اسم المركز')
        self.fields['city'].label = _('المدينة')
        self.fields['address'].label = _('العنوان')
        self.fields['phone_number'].label = _('رقم الهاتف')
        self.fields['email'].label = _('البريد الإلكتروني')
        self.fields['is_active'].label = _('نشط')
        
        # Set help texts
        self.fields['name'].help_text = _('أدخل اسم المركز الطبي')
        self.fields['city'].help_text = _('اختر المدينة')
        self.fields['address'].help_text = _('أدخل عنوان المركز بالتفصيل')
        self.fields['phone_number'].help_text = _('أدخل رقم هاتف المركز')
        self.fields['email'].help_text = _('أدخل البريد الإلكتروني للمركز')
        self.fields['is_active'].help_text = _('هل المركز نشط؟')
        
        # Set empty labels
        self.fields['city'].empty_label = _('اختر المدينة')


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    form = CenterForm
    list_display = ('get_center_name', 'city', 'phone_number', 'is_active', 'doctors_count', 'staff_count', 'created_at')
    list_filter = (CenterListFilter, 'city', 'is_active', 'created_at')
    search_fields = ('name', 'address', 'phone_number', 'email', 'city__name')
    ordering = ('name',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'created_at'
    preserve_filters = True
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    def get_center_name(self, obj):
        """Display center name with styling"""
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            obj.name
        )
    get_center_name.short_description = _('اسم المركز')
    
    def doctors_count(self, obj):
        count = obj.doctors.count()
        return format_html(
            '<span style="color: #059669; font-weight: 600;">{}</span>',
            count
        )
    doctors_count.short_description = _('عدد الأطباء')
    
    def staff_count(self, obj):
        count = obj.staff.count()
        return format_html(
            '<span style="color: #059669; font-weight: 600;">{}</span>',
            count
        )
    staff_count.short_description = _('عدد الموظفين')
    
    class Meta:
        verbose_name = _('المركز الطبي')
        verbose_name_plural = _('المراكز الطبية')


class DoctorListFilter(admin.SimpleListFilter):
    title = _('حالة الطبيب')
    parameter_name = 'doctor_status'

    def lookups(self, request, model_admin):
        return (
            ('available', _('متاح')),
            ('unavailable', _('غير متاح')),
            ('experienced', _('خبرة عالية (10+ سنوات)')),
            ('new', _('جديد (أقل من 5 سنوات)')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'available':
            return queryset.filter(is_available=True)
        if self.value() == 'unavailable':
            return queryset.filter(is_available=False)
        if self.value() == 'experienced':
            return queryset.filter(experience_years__gte=10)
        if self.value() == 'new':
            return queryset.filter(experience_years__lt=5)


class DoctorForm(forms.ModelForm):
    """Custom form for Doctor with enhanced functionality"""
    
    class Meta:
        model = Doctor
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'center': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'specialization': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل رقم الترخيص'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد سنوات الخبرة',
                'style': 'max-width: 150px !important;'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter user field to only show users with DOCTOR role
        from apps.accounts.models import User
        self.fields['user'].queryset = User.objects.filter(role='DOCTOR')
        
        # Set Arabic labels
        self.fields['user'].label = _('الطبيب')
        self.fields['center'].label = _('المركز')
        self.fields['specialization'].label = _('التخصص')
        self.fields['license_number'].label = _('رقم الترخيص')
        self.fields['experience_years'].label = _('سنوات الخبرة')
        self.fields['is_available'].label = _('متاح')
        
        # Set help texts
        self.fields['user'].help_text = _('اختر الطبيب')
        self.fields['center'].help_text = _('اختر المركز')
        self.fields['specialization'].help_text = _('اختر تخصص الطبيب')
        self.fields['license_number'].help_text = _('أدخل رقم ترخيص الطبيب')
        self.fields['experience_years'].help_text = _('عدد سنوات الخبرة')
        self.fields['is_available'].help_text = _('هل الطبيب متاح للعمل؟')
        
        # Set empty labels
        self.fields['user'].empty_label = _('اختر الطبيب')
        self.fields['center'].empty_label = _('اختر المركز')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorForm
    list_display = ('get_doctor_name', 'get_center_info', 'specialization', 'license_number', 'get_experience_badge', 'get_availability_status', 'created_at')
    list_filter = (DoctorListFilter, 'center', 'specialization', 'is_available', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'license_number', 'specialization', 'center__name')
    ordering = ('user__first_name',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'created_at'
    preserve_filters = True
    list_select_related = ('user', 'center')
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    def get_doctor_name(self, obj):
        """Display doctor name with enhanced styling"""
        name = f"د. {obj.user.first_name} {obj.user.last_name}"
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<i class="fas fa-user-md" style="color: #059669; font-size: 16px;"></i>'
            '<span style="color: #1f2937; font-weight: 600; font-size: 14px;">{}</span>'
            '</div>',
            name
        )
    get_doctor_name.short_description = _('اسم الطبيب')
    get_doctor_name.admin_order_field = 'user__first_name'
    
    def get_center_info(self, obj):
        """Display center information"""
        if obj.center:
            return format_html(
                '<div style="display: flex; flex-direction: column; gap: 2px;">'
                '<span style="color: #1f2937; font-weight: 600; font-size: 13px;">{}</span>'
                '<span style="color: #6b7280; font-size: 11px;">{}</span>'
                '</div>',
                obj.center.name, obj.center.city.name if obj.center.city else "غير محدد"
            )
        return format_html('<span style="color: #9ca3af;">غير محدد</span>')
    get_center_info.short_description = _('المركز')
    get_center_info.admin_order_field = 'center__name'
    
    def get_experience_badge(self, obj):
        """Display experience with a colored badge"""
        years = obj.experience_years or 0
        if years >= 10:
            color = '#059669'
            bg_color = '#d1fae5'
            icon = 'fas fa-star'
        elif years >= 5:
            color = '#d97706'
            bg_color = '#fef3c7'
            icon = 'fas fa-medal'
        else:
            color = '#6b7280'
            bg_color = '#f3f4f6'
            icon = 'fas fa-user-graduate'
        
        return format_html(
            '<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: {}; color: {}; border-radius: 6px; font-size: 12px; font-weight: 600;">'
            '<i class="{}"></i>'
            '{} سنوات'
            '</span>',
            bg_color, color, icon, years
        )
    get_experience_badge.short_description = _('الخبرة')
    get_experience_badge.admin_order_field = 'experience_years'
    
    def get_availability_status(self, obj):
        """Display availability status with a modern badge"""
        if obj.is_available:
            return format_html(
                '<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: #d1fae5; color: #065f46; border-radius: 6px; font-size: 12px; font-weight: 600;">'
                '<i class="fas fa-check-circle"></i>'
                'متاح'
                '</span>'
            )
        else:
            return format_html(
                '<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: #fee2e2; color: #991b1b; border-radius: 6px; font-size: 12px; font-weight: 600;">'
                '<i class="fas fa-times-circle"></i>'
                'غير متاح'
                '</span>'
            )
    get_availability_status.short_description = _('الحالة')
    get_availability_status.admin_order_field = 'is_available'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _('إدارة الأطباء - البحث والفلترة المتقدمة')
        
        # Add centers list for filter sidebar
        from apps.hospital.models import Center
        extra_context['centers'] = Center.objects.select_related('city').all()[:20]  # Limit to first 20 centers
        
        # Add search statistics
        if request.GET.get('q'):
            search_term = request.GET.get('q')
            total_results = self.get_queryset(request).count()
            extra_context['search_info'] = f'تم العثور على {total_results} نتيجة للبحث عن "{search_term}"'
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user', 'center', 'center__city')
    
    class Meta:
        verbose_name = _('الطبيب')
        verbose_name_plural = _('الأطباء')


class StaffForm(forms.ModelForm):
    """Custom form for Staff with enhanced functionality"""
    
    # Add city field for filtering centers
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label="اختر المدينة أولاً",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;',
            'onchange': 'filterCenters()'
        })
    )
    
    class Meta:
        model = Staff
        fields = ['user', 'center', 'department', 'employee_id', 'salary', 'is_active']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'center': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل رقم الموظف'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الراتب',
                'style': 'max-width: 200px !important;'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Show all users, not just STAFF role (since we need to create staff first)
        from apps.accounts.models import User
        self.fields['user'].queryset = User.objects.all()
        
        # Set Arabic labels
        self.fields['city'].label = _('المدينة')
        self.fields['user'].label = _('الموظف')
        self.fields['center'].label = _('المركز')
        self.fields['department'].label = _('القسم')
        self.fields['employee_id'].label = _('رقم الموظف')
        self.fields['salary'].label = _('الراتب')
        self.fields['is_active'].label = _('نشط')
        
        # Set help texts
        self.fields['city'].help_text = _('اختر المدينة أولاً لتصفية المراكز')
        self.fields['user'].help_text = _('اختر الموظف')
        self.fields['center'].help_text = _('اختر المركز (يظهر بعد اختيار المدينة)')
        self.fields['department'].help_text = _('اختر القسم')
        self.fields['employee_id'].help_text = _('أدخل رقم الموظف')
        self.fields['salary'].help_text = _('أدخل الراتب')
        self.fields['is_active'].help_text = _('هل الموظف نشط؟')
        
        # Set empty labels
        self.fields['city'].empty_label = _('اختر المدينة أولاً')
        self.fields['user'].empty_label = _('اختر الموظف')
        self.fields['center'].empty_label = _('اختر المركز')
        self.fields['department'].empty_label = _('اختر القسم')
        
        # Reorder fields to put city after center
        field_order = ['user', 'center', 'city', 'department', 'employee_id', 'salary', 'is_active']
        self.fields = {k: self.fields[k] for k in field_order if k in self.fields}


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    form = StaffForm
    list_display = ('get_staff_name', 'center', 'department', 'employee_id', 'is_active', 'created_at')
    list_filter = ('center', 'department', 'is_active', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'employee_id')
    ordering = ('user__first_name',)
    raw_id_fields = ()
    list_per_page = 25
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    # Define field order for the form
    fields = ('user', 'city' ,'center', 'department', 'employee_id', 'salary', 'is_active')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add RelatedFieldWidgetWrapper for user field (simplified - no add button)
        if 'user' in form.base_fields:
            from apps.accounts.models import User
            # Get the field from the Staff model, not User model
            user_field = Staff._meta.get_field('user')
            form.base_fields['user'].widget = RelatedFieldWidgetWrapper(
                form.base_fields['user'].widget,
                user_field.remote_field,
                admin_site=admin.site,
                can_add_related=False,  # Disable built-in add button
                can_change_related=True,
                can_delete_related=False,
                can_view_related=True,
            )
        
        # City field doesn't need RelatedFieldWidgetWrapper since it's not a model field
        # The quick add functionality will be handled by the universal quick add popup system
        
        # Add RelatedFieldWidgetWrapper for center field
        if 'center' in form.base_fields:
            center_field = Staff._meta.get_field('center')
            form.base_fields['center'].widget = RelatedFieldWidgetWrapper(
                form.base_fields['center'].widget,
                center_field.remote_field,
                admin_site=admin.site,
                can_add_related=True,  # Enable add button for centers
                can_change_related=True,
                can_delete_related=False,
                can_view_related=True,
            )
        
        return form
    
    class Media:
        js = ('admin/js/staff_form.js',)
    
    def get_staff_name(self, obj):
        """Display staff name in Arabic format with styling"""
        name = f"{obj.user.first_name} {obj.user.last_name}"
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            name
        )
    get_staff_name.short_description = _('اسم الموظف')
    
    class Meta:
        verbose_name = _('الموظف')
        verbose_name_plural = _('الموظفون')


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('get_medicine_name', 'generic_name', 'dosage_form', 'strength', 'manufacturer', 'is_prescription_required', 'is_active', 'created_at')
    list_filter = ('dosage_form', 'is_prescription_required', 'is_active', 'created_at')
    search_fields = ('name', 'generic_name', 'manufacturer')
    ordering = ('name',)
    list_per_page = 25
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    def get_medicine_name(self, obj):
        """Display medicine name with styling"""
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            obj.name
        )
    get_medicine_name.short_description = _('اسم الدواء')
    
    class Meta:
        verbose_name = _('الدواء')
        verbose_name_plural = _('الأدوية')


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('get_disease_name', 'category', 'icd_code', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'symptoms', 'icd_code')
    ordering = ('name',)
    list_per_page = 25
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    def get_disease_name(self, obj):
        """Display disease name with styling"""
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            obj.name
        )
    get_disease_name.short_description = _('اسم المرض')
    
    class Meta:
        verbose_name = _('المرض')
        verbose_name_plural = _('الأمراض')
