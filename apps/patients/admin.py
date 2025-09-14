from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Q
from django import forms
from .models import Patient, PatientDisease, Test, Treatment, TreatmentMedicine, Surgery, Visit
from apps.hospital.models import Doctor, City, Center, Disease


class PatientForm(forms.ModelForm):
    """Custom form for Patient with enhanced user display"""
    
    # Additional fields for admin role
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False,
        empty_label="اختر المدينة",
        label=_('المدينة'),
        help_text=_('اختر المدينة لتصفية المستشفيات'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
        })
    )
    
    center = forms.ModelChoiceField(
        queryset=Center.objects.none(),  # Start with empty queryset
        required=False,
        empty_label="اختر المستشفى",
        label=_('المستشفى'),
        help_text=_('اختر المستشفى لتصفية الأطباء'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
        })
    )
    
    class Meta:
        model = Patient
        fields = '__all__'
        # No exclusions - let all fields be validated normally
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
            }),
        }
    
    def clean_patient_id(self):
        """Validate phone number format and uniqueness"""
        phone_number = self.cleaned_data.get('patient_id')
        print(f"🔍 [VALIDATION] clean_patient_id called with: '{phone_number}'")
        print(f"🔍 [VALIDATION] Phone number type: {type(phone_number)}")
        
        if not phone_number:
            print("❌ [VALIDATION] Phone number is empty")
            raise forms.ValidationError('رقم الهاتف مطلوب')
        
        # Remove any non-digit characters
        original_phone = phone_number
        phone_number = ''.join(filter(str.isdigit, phone_number))
        print(f"🔍 [VALIDATION] Cleaned phone: '{original_phone}' -> '{phone_number}'")
        
        # Check if it's exactly 11 digits
        if len(phone_number) != 11:
            print(f"❌ [VALIDATION] Phone length is not 11: '{phone_number}' (length: {len(phone_number)})")
            raise forms.ValidationError('رقم الهاتف يجب أن يكون 11 رقماً بالضبط')
        
        # Check if it starts with valid Iraqi mobile prefixes
        valid_prefixes = ['07', '01']  # Iraqi mobile prefixes
        if not any(phone_number.startswith(prefix) for prefix in valid_prefixes):
            print(f"❌ [VALIDATION] Phone doesn't start with 07 or 01: '{phone_number}'")
            raise forms.ValidationError('رقم الهاتف يجب أن يبدأ بـ 07 أو 01 (أرقام الهواتف العراقية)')
        
        # Check uniqueness (exclude current instance if editing)
        existing_patient = Patient.objects.filter(patient_id=phone_number)
        if self.instance.pk:
            existing_patient = existing_patient.exclude(pk=self.instance.pk)
        
        if existing_patient.exists():
            print(f"❌ [VALIDATION] Phone number already exists: '{phone_number}'")
            raise forms.ValidationError('رقم الهاتف هذا مستخدم بالفعل لمريض آخر')
        
        print(f"✅ [VALIDATION] Phone number validation passed: '{phone_number}'")
        return phone_number
    
    def clean_patient_name(self):
        """Clean method for patient_name field - validate and return the submitted value"""
        patient_name = self.cleaned_data.get('patient_name', '')
        print(f"🔍 [VALIDATION] clean_patient_name called with: '{patient_name}'")
        print(f"🔍 [VALIDATION] Patient name type: {type(patient_name)}")
        print(f"🔍 [VALIDATION] Patient name length: {len(patient_name) if patient_name else 0}")
        
        if not patient_name:
            print("❌ [VALIDATION] Patient name is empty")
            raise forms.ValidationError('اسم المريض مطلوب')
        
        if len(patient_name.strip()) < 2:
            print("❌ [VALIDATION] Patient name is too short")
            raise forms.ValidationError('اسم المريض يجب أن يكون على الأقل حرفين')
        
        # Check for invalid characters
        if not patient_name.strip():
            print("❌ [VALIDATION] Patient name is only whitespace")
            raise forms.ValidationError('اسم المريض لا يمكن أن يكون فارغاً')
        
        print(f"✅ [VALIDATION] Patient name validation passed: '{patient_name}'")
        return patient_name.strip()
    
    def clean(self):
        """Additional form validation"""
        print(f"🔍 [VALIDATION] clean() method called")
        try:
            cleaned_data = super().clean()
            print(f"🔍 [VALIDATION] cleaned_data keys: {list(cleaned_data.keys())}")
            
            # Debug: Print all form data
            print(f"🔍 [VALIDATION] Form data keys: {list(self.data.keys()) if hasattr(self, 'data') and self.data else 'No data'}")
            if hasattr(self, 'data') and self.data:
                print(f"🔍 [VALIDATION] Form data values:")
                for key, value in self.data.items():
                    print(f"    {key}: {value}")
        except Exception as e:
            print(f"❌ [VALIDATION] Exception in clean(): {e}")
            print(f"❌ [VALIDATION] Exception type: {type(e)}")
            raise
        
        # Ensure user field is set for new patients
        if not self.instance.pk and self.request:
            print(f"🔍 [VALIDATION] Setting user field to: {self.request.user}")
            cleaned_data['user'] = self.request.user
        
        # Validate doctor field - either direct selection or via city/center
        doctor = cleaned_data.get('doctor')
        city = cleaned_data.get('city')
        center = cleaned_data.get('center')
        
        print(f"🔍 [VALIDATION] Doctor field: {doctor}")
        print(f"🔍 [VALIDATION] City: {city}, Center: {center}")
        print(f"🔍 [VALIDATION] All cleaned_data keys: {list(cleaned_data.keys())}")
        
        if not doctor:
            print(f"🔍 [VALIDATION] No doctor selected, checking city/center")
            
            # Check if city and center are provided in the form data
            if city and center:
                print(f"🔍 [VALIDATION] City and center provided: {city}, {center}")
                # Get first available doctor from selected center
                available_doctors = Doctor.objects.filter(center=center)
                print(f"🔍 [VALIDATION] Available doctors: {available_doctors.count()}")
                if available_doctors.exists():
                    selected_doctor = available_doctors.first()
                    cleaned_data['doctor'] = selected_doctor
                    print(f"✅ [VALIDATION] Auto-selected doctor: {selected_doctor}")
                else:
                    print(f"❌ [VALIDATION] No doctors available in center")
                    raise forms.ValidationError('لا يوجد أطباء متاحين في المستشفى المحدد')
            else:
                print(f"❌ [VALIDATION] Missing city or center - City: {city}, Center: {center}")
                # More specific error message
                if not city and not center:
                    raise forms.ValidationError('يجب اختيار الطبيب أو المدينة والمستشفى')
                elif not city:
                    raise forms.ValidationError('يجب اختيار المدينة')
                elif not center:
                    raise forms.ValidationError('يجب اختيار المستشفى')
        else:
            print(f"✅ [VALIDATION] Doctor selected: {doctor}")
            
        # Final check - ensure we have a doctor
        if not cleaned_data.get('doctor'):
            print(f"❌ [VALIDATION] No doctor assigned after validation")
            raise forms.ValidationError('يجب اختيار الطبيب أو المدينة والمستشفى')
        
        # Validate date of birth
        date_of_birth = cleaned_data.get('date_of_birth')
        print(f"🔍 [VALIDATION] Date of birth: {date_of_birth}")
        print(f"🔍 [VALIDATION] Date of birth type: {type(date_of_birth)}")
        
        if date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            print(f"🔍 [VALIDATION] Calculated age: {age}")

            if age < 0:
                print(f"❌ [VALIDATION] Age is negative: {age}")
                raise forms.ValidationError('تاريخ الميلاد لا يمكن أن يكون في المستقبل')

            if age > 150:
                print(f"❌ [VALIDATION] Age is too high: {age}")
                raise forms.ValidationError('العمر المدخل غير منطقي')
            
            print(f"✅ [VALIDATION] Date of birth validation passed: {date_of_birth} (age: {age})")
        else:
            print(f"❌ [VALIDATION] Date of birth is missing")
            raise forms.ValidationError('تاريخ الميلاد مطلوب')

        print(f"✅ [VALIDATION] All validations passed!")
        print(f"🔍 [VALIDATION] Final cleaned_data keys: {list(cleaned_data.keys())}")
        
        # Debug: Check if there are any validation errors
        if hasattr(self, 'errors') and self.errors:
            print(f"❌ [VALIDATION] Form has errors: {self.errors}")
        if hasattr(self, 'non_field_errors') and self.non_field_errors():
            print(f"❌ [VALIDATION] Form has non-field errors: {self.non_field_errors()}")
        
        return cleaned_data
    
    def _post_clean(self):
        """Override _post_clean to handle user field for new patients"""
        super()._post_clean()
        
        # For new patients, ensure user is set
        if not self.instance.pk and self.request:
            try:
                # Check if user is already set
                if not self.instance.user:
                    self.instance.user = self.request.user
            except:
                # If user is not set, set it
                self.instance.user = self.request.user
    
    def save(self, commit=True):
        """Override save method"""
        instance = super().save(commit=commit)
        return instance
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        print(f"🔍 [FORM INIT] PatientForm initialized")
        print(f"🔍 [FORM INIT] Data provided: {bool(kwargs.get('data'))}")
        if kwargs.get('data'):
            print(f"🔍 [FORM INIT] Data keys: {list(kwargs['data'].keys())}")
            print(f"🔍 [FORM INIT] City in data: {'city' in kwargs['data']}")
            print(f"🔍 [FORM INIT] Center in data: {'center' in kwargs['data']}")
            print(f"🔍 [FORM INIT] Doctor in data: {'doctor' in kwargs['data']}")
        
        # Filter user field to only show users with PATIENT role
        from apps.accounts.models import User
        self.fields['user'].queryset = User.objects.filter(role='PATIENT')
        
        # For admin users, also include the current admin user in the queryset
        if self.request and self.request.user.role == 'ADMIN':
            admin_user = self.request.user
            print(f"🔍 [FORM INIT] Admin user: {admin_user} (ID: {admin_user.id})")
            print(f"🔍 [FORM INIT] Current user queryset: {list(self.fields['user'].queryset.values_list('id', flat=True))}")
            if admin_user not in self.fields['user'].queryset:
                # Add admin user to the queryset
                self.fields['user'].queryset = User.objects.filter(
                    Q(role='PATIENT') | Q(id=admin_user.id)
                )
                print(f"🔍 [FORM INIT] Updated user queryset: {list(self.fields['user'].queryset.values_list('id', flat=True))}")
        
        # Set Arabic labels and help texts
        self.fields['user'].label = _('المريض')
        self.fields['user'].empty_label = _('اختر المريض')
        
        # Configure patient_id field for phone number input
        self.fields['patient_id'].help_text = _('أدخل رقم هاتف المريض (11 رقماً فقط، يجب أن يبدأ بـ 07 أو 01)')
        self.fields['patient_id'].widget = forms.TextInput(attrs={
            'type': 'tel',
            'pattern': '^0[17][0-9]{9}$',
            'maxlength': '11',
            'minlength': '11',
            'placeholder': '07xxxxxxxxx',
            'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "").slice(0, 11);',
            'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'
        })
        
        if self.request:
            # Customize user field display for both new and existing patients
            if not self.instance.pk:  # New patient
                # Set the initial value to the current user
                self.fields['user'].initial = self.request.user
                self.fields['user'].widget = forms.HiddenInput()
                self.fields['user'].required = False  # Make it not required since we set it in clean()
                # Remove from required fields
                if hasattr(self.fields['user'], 'required') and self.fields['user'].required:
                    self.fields['user'].required = False
                
                user_display = f"{self.request.user.get_full_name()} ({self.request.user.email})"
                help_text = _('سيتم ربط المريض بحسابك الحالي')
            else:  # Existing patient
                # Show the current user of the patient
                if self.instance.user:
                    user_display = f"{self.instance.user.get_full_name()} ({self.instance.user.email})"
                    help_text = _('المستخدم المرتبط بهذا المريض')
                else:
                    user_display = _('لا يوجد مستخدم مرتبط')
                    help_text = _('هذا المريض غير مرتبط بأي مستخدم')
            
            # Create a custom widget for display only
            class DisplayOnlyWidget(forms.Widget):
                def render(self, name, value, attrs=None, renderer=None):
                    return f'''
                    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 8px 12px; border-radius: 4px; color: #495057; min-height: 38px; display: flex; align-items: center;">
                        {user_display}
                    </div>
                    '''
            
            self.fields['user_display'] = forms.CharField(
                initial=user_display,
                widget=DisplayOnlyWidget(),
                help_text=help_text,
                required=False
            )
            
            # Convert user_display to patient name input field
            if not self.instance.pk:  # New patient
                patient_name_initial = ''
                patient_name_help = _('أدخل اسم المريض الكامل')
            else:  # Existing patient
                # Use actual patient name, fallback to user name if patient_name is empty
                if self.instance.patient_name and self.instance.patient_name.strip():
                    patient_name_initial = self.instance.patient_name
                else:
                    patient_name_initial = f"{self.instance.user.first_name} {self.instance.user.last_name}".strip()
                patient_name_help = _('اسم المريض')
            
            # Replace user_display with patient name input
            self.fields['patient_name'] = forms.CharField(
                initial=patient_name_initial,
                widget=forms.TextInput(attrs={
                    'placeholder': 'أدخل اسم المريض الكامل',
                    'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
                }),
                help_text=patient_name_help,
                required=True,  # Make it required
                label=_('اسم المريض')
            )
            
            # Remove user_display field
            if 'user_display' in self.fields:
                del self.fields['user_display']
            
            # Ensure the field has the correct value
            if 'data' not in kwargs or not kwargs.get('data'):
                self.initial['patient_name'] = patient_name_initial
            
            # Filter doctors based on user role
            if self.request.user.role == 'ADMIN':
                # Admin can see all doctors and has city/hospital selection
                self.fields['doctor'].queryset = Doctor.objects.select_related('user', 'center').all()
                # Make doctor field not required initially for admin
                self.fields['doctor'].required = False
                self.fields['doctor'].empty_label = "اختر الطبيب"
                self.fields['doctor'].help_text = _('اختر الطبيب أو استخدم المدينة والمستشفى للتصفية')
                
                # Initialize center field with all centers
                self.fields['center'].queryset = Center.objects.all()
                
                # Apply styling to select widgets
                self.fields['city'].widget.attrs.update({
                    'onchange': 'filterCenters()',
                    'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
                })
                self.fields['center'].widget.attrs.update({
                    'onchange': 'filterDoctors()',
                    'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
                })
                self.fields['doctor'].widget.attrs.update({
                    'onchange': 'updateDoctorInfo()',
                    'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
                })
                
            elif self.request.user.role == 'DOCTOR':
                # Doctor can only assign patients to themselves
                self.fields['doctor'].queryset = Doctor.objects.filter(user=self.request.user)
                self.fields['doctor'].initial = Doctor.objects.filter(user=self.request.user).first()
                self.fields['doctor'].help_text = _('سيتم ربط المريض بحسابك كطبيب')
                
                # Apply styling to doctor field
                self.fields['doctor'].widget.attrs.update({
                    'readonly': True,
                    'disabled': True,
                    'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #f8f9fa;'
                })
                
                # Hide city and hospital fields for doctor
                self.fields['city'].widget = forms.HiddenInput()
                self.fields['center'].widget = forms.HiddenInput()
                
            elif self.request.user.role == 'STAFF':
                # Staff can assign to doctors in their center
                if hasattr(self.request.user, 'staff_profile') and self.request.user.staff_profile.center:
                    self.fields['doctor'].queryset = Doctor.objects.filter(center=self.request.user.staff_profile.center)
                    self.fields['doctor'].empty_label = "اختر الطبيب"
                    self.fields['doctor'].help_text = _('اختر طبيب من مستشفاك')
                    
                    # Apply styling to doctor field
                    self.fields['doctor'].widget.attrs.update({
                        'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
                    })
                else:
                    self.fields['doctor'].queryset = Doctor.objects.none()
                
                # Hide city and hospital fields for staff
                self.fields['city'].widget = forms.HiddenInput()
                self.fields['center'].widget = forms.HiddenInput()


class PatientListFilter(admin.SimpleListFilter):
    title = _('حالة المريض')
    parameter_name = 'patient_status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('نشط')),
            ('inactive', _('غير نشط')),
            ('recent', _('جديد (آخر 7 أيام)')),
            ('old', _('قديم (أكثر من سنة)')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)
        if self.value() == 'recent':
            from django.utils import timezone
            from datetime import timedelta
            return queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
        if self.value() == 'old':
            from django.utils import timezone
            from datetime import timedelta
            return queryset.filter(created_at__lt=timezone.now() - timedelta(days=365))


class DoctorListFilter(admin.SimpleListFilter):
    title = _('الطبيب')
    parameter_name = 'doctor'

    def lookups(self, request, model_admin):
        from apps.hospital.models import Doctor
        doctors = Doctor.objects.all()
        return [(doctor.id, doctor.user.get_full_name()) for doctor in doctors if doctor.user]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(doctor_id=self.value())


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    form = PatientForm
    list_display = ('get_patient_name', 'patient_id', 'get_doctor_info', 'get_age', 'gender', 'blood_group', 'get_status_badge', 'created_at')
    list_display_links = ('get_patient_name', 'patient_id')  # Make these clickable for editing
    list_filter = (PatientListFilter, DoctorListFilter, 'gender', 'blood_group', 'is_active', 'created_at')
    search_fields = ('patient_name', 'user__first_name', 'user__last_name', 'user__email', 'patient_id', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'doctor__user__first_name', 'doctor__user__last_name')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'created_at'
    preserve_filters = True
    list_select_related = ('user', 'doctor', 'doctor__user')
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    # Enable actions for bulk operations
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        """Mark selected patients as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} patients marked as active.')
    mark_as_active.short_description = "Mark selected patients as active"
    
    def mark_as_inactive(self, request, queryset):
        """Mark selected patients as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} patients marked as inactive.')
    mark_as_inactive.short_description = "Mark selected patients as inactive"
    
    # Define field order with doctor field after hospital
    fieldsets = (
        (None, {
            'fields': ('patient_name', 'user', 'patient_id', 'date_of_birth', 'gender', 'blood_group', 'city', 'center', 'doctor')
        }),
        ('معلومات الاتصال', {
            'fields': ('address', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('المعلومات الطبية', {
            'fields': ('medical_history', 'allergies', 'is_active')
        }),
    )
    
    # Enhanced search with better performance
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            # Use select_related for better performance
            queryset = queryset.select_related('user', 'doctor', 'doctor__user')
            queryset = queryset.filter(
                Q(patient_name__icontains=search_term) |
                Q(user__first_name__icontains=search_term) |
                Q(user__last_name__icontains=search_term) |
                Q(user__email__icontains=search_term) |
                Q(patient_id__icontains=search_term) |
                Q(address__icontains=search_term) |
                Q(emergency_contact_name__icontains=search_term) |
                Q(emergency_contact_phone__icontains=search_term) |
                Q(doctor__user__first_name__icontains=search_term) |
                Q(doctor__user__last_name__icontains=search_term) |
                Q(doctor__specialization__icontains=search_term)
            )
        return queryset, False
    
    def get_patient_name(self, obj):
        """Display patient name with enhanced styling and profile link"""
        from django.urls import reverse
        # Use patient_name if available, otherwise fall back to user name
        if obj.patient_name and obj.patient_name.strip():
            name = obj.patient_name
        else:
            name = f"{obj.user.first_name} {obj.user.last_name}"
        
        profile_url = reverse('admin_patient_profile', args=[obj.id])
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<i class="fas fa-user" style="color: #667eea; font-size: 14px;"></i>'
            '<span style="color: #1f2937; font-weight: 600; font-size: 14px;">{}</span>'
            '<a href="{}" style="margin-left: 8px; color: #10b981; text-decoration: none;" title="عرض الملف الشخصي">'
            '<i class="fas fa-user-circle" style="font-size: 16px;"></i>'
            '</a>'
            '</div>',
            name, profile_url
        )
    get_patient_name.short_description = _('اسم المريض')
    get_patient_name.admin_order_field = 'user__first_name'
    
    def get_doctor_info(self, obj):
        """Display doctor information with specialization"""
        if obj.doctor:
            doctor_name = f"د. {obj.doctor.user.first_name} {obj.doctor.user.last_name}"
            specialization = obj.doctor.specialization or "غير محدد"
            return format_html(
                '<div style="display: flex; flex-direction: column; gap: 2px;">'
                '<span style="color: #1f2937; font-weight: 600; font-size: 13px;">{}</span>'
                '<span style="color: #6b7280; font-size: 11px;">{}</span>'
                '</div>',
                doctor_name, specialization
            )
        return format_html('<span style="color: #9ca3af;">غير محدد</span>')
    get_doctor_info.short_description = _('الطبيب')
    get_doctor_info.admin_order_field = 'doctor__user__first_name'
    
    def get_age(self, obj):
        """Calculate and display patient age"""
        if obj.date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
            return format_html(
                '<div style="display: flex; align-items: center; gap: 6px;">'
                '<i class="fas fa-birthday-cake" style="color: #f59e0b; font-size: 12px;"></i>'
                '<span style="color: #374151; font-weight: 500;">{} سنة</span>'
                '</div>',
                age
            )
        return format_html('<span style="color: #9ca3af;">غير محدد</span>')
    get_age.short_description = _('العمر')
    
    def get_status_badge(self, obj):
        """Display status with a modern badge"""
        if obj.is_active:
            return format_html(
                '<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: #d1fae5; color: #065f46; border-radius: 6px; font-size: 12px; font-weight: 600;">'
                '<i class="fas fa-check-circle"></i>'
                'نشط'
                '</span>'
            )
        else:
            return format_html(
                '<span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: #fee2e2; color: #991b1b; border-radius: 6px; font-size: 12px; font-weight: 600;">'
                '<i class="fas fa-times-circle"></i>'
                'غير نشط'
                '</span>'
            )
    get_status_badge.short_description = _('الحالة')
    get_status_badge.admin_order_field = 'is_active'
    
    def get_form(self, request, obj=None, **kwargs):
        """Return custom form with request context"""
        form_class = self.form
        
        class FormWithRequest(form_class):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)
                
                # Ensure date_of_birth field has proper date input attributes
                if 'date_of_birth' in self.fields:
                    self.fields['date_of_birth'].widget.attrs.update({
                        'type': 'date',
                        'class': 'form-control',
                        'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
                    })
        
        return FormWithRequest


class VisitForm(forms.ModelForm):
    """Custom form for Visit with enhanced functionality and cascading dropdowns"""
    
    class Meta:
        model = Visit
        fields = '__all__'
        # Include the additional fields for cascading dropdown
        fields = ['patient', 'doctor', 'visit_type', 'visit_date', 'status', 
                 'chief_complaint', 'diagnosis', 'treatment_plan', 'notes', 'follow_up_date']
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'visit_type': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'visit_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'style': 'max-width: 250px !important;'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'chief_complaint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل الشكوى الرئيسية'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل التشخيص'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل خطة العلاج'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل ملاحظات إضافية'
            }),
            'follow_up_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'style': 'max-width: 250px !important;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request if provided
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Ensure city and center fields are added to the form
        if 'city' not in self.fields:
            self.fields['city'] = forms.ModelChoiceField(
                queryset=City.objects.all(),
                required=False,
                empty_label="اختر المدينة",
                label=_('المدينة'),
                help_text=_('اختر المدينة لتصفية المستشفيات'),
                widget=forms.Select(attrs={
                    'class': 'form-control',
                    'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
                })
            )
        
        if 'center' not in self.fields:
            self.fields['center'] = forms.ModelChoiceField(
                queryset=Center.objects.none(),
                required=False,
                empty_label="اختر المستشفى",
                label=_('المستشفى'),
                help_text=_('اختر المستشفى لتصفية الأطباء'),
                widget=forms.Select(attrs={
                    'class': 'form-control',
                    'style': 'width: 100%; padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; color: #000; background-color: #fff;'
                })
            )
        
        # Reorder fields to show city, center, then doctor
        field_order = ['patient', 'city', 'center', 'doctor', 'visit_type', 'visit_date', 'status', 
                      'chief_complaint', 'diagnosis', 'treatment_plan', 'notes', 'follow_up_date']
        
        # Reorder the fields
        ordered_fields = {}
        for field_name in field_order:
            if field_name in self.fields:
                ordered_fields[field_name] = self.fields[field_name]
        
        # Add any remaining fields that weren't in the order
        for field_name, field in self.fields.items():
            if field_name not in ordered_fields:
                ordered_fields[field_name] = field
        
        self.fields = ordered_fields
        
        # Set Arabic labels
        self.fields['patient'].label = _('المريض')
        self.fields['doctor'].label = _('الطبيب')
        self.fields['visit_type'].label = _('نوع الزيارة')
        self.fields['visit_date'].label = _('تاريخ ووقت الزيارة')
        self.fields['status'].label = _('حالة الزيارة')
        self.fields['chief_complaint'].label = _('الشكوى الرئيسية')
        self.fields['diagnosis'].label = _('التشخيص')
        self.fields['treatment_plan'].label = _('خطة العلاج')
        self.fields['notes'].label = _('ملاحظات إضافية')
        self.fields['follow_up_date'].label = _('تاريخ المتابعة')
        
        # Set help texts
        self.fields['patient'].help_text = _('اختر المريض')
        self.fields['doctor'].help_text = _('اختر الطبيب')
        self.fields['visit_type'].help_text = _('نوع الزيارة')
        self.fields['visit_date'].help_text = _('تاريخ ووقت الزيارة')
        self.fields['status'].help_text = _('حالة الزيارة الحالية')
        self.fields['chief_complaint'].help_text = _('وصف المشكلة أو السبب في الزيارة')
        self.fields['diagnosis'].help_text = _('التشخيص الطبي')
        self.fields['treatment_plan'].help_text = _('العلاج الموصى به')
        self.fields['notes'].help_text = _('ملاحظات إضافية')
        self.fields['follow_up_date'].help_text = _('تاريخ المتابعة المقترح')
        
        # Set empty labels
        self.fields['patient'].empty_label = _('اختر المريض')
        self.fields['doctor'].empty_label = _('اختر الطبيب')
        self.fields['visit_type'].empty_label = _('اختر نوع الزيارة')
        self.fields['status'].empty_label = _('اختر الحالة')
        
        # If editing an existing visit, populate the cascading fields
        if self.instance and self.instance.pk and self.instance.doctor:
            self.fields['city'].initial = self.instance.doctor.center.city
            self.fields['center'].queryset = Center.objects.filter(city=self.instance.doctor.center.city)
            self.fields['center'].initial = self.instance.doctor.center
    
    def clean(self):
        """Clean method to handle city and center fields"""
        cleaned_data = super().clean()
        
        # Remove city and center from cleaned_data since they're not model fields
        cleaned_data.pop('city', None)
        cleaned_data.pop('center', None)
        
        return cleaned_data


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    form = VisitForm
    list_display = ('get_patient_name', 'doctor', 'visit_type', 'visit_date', 'get_status_badge', 'chief_complaint_short', 'created_at')
    list_display_links = ('get_patient_name', 'visit_date')  # Make these clickable for editing
    list_filter = ('visit_type', 'status', 'visit_date', 'created_at')
    search_fields = ('patient__patient_name', 'patient__patient_id', 'doctor__user__first_name', 'doctor__user__last_name', 'chief_complaint', 'diagnosis')
    ordering = ('-visit_date',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'visit_date'
    preserve_filters = True
    list_select_related = ('patient', 'patient__user', 'doctor', 'doctor__user')
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    # Define field order for the form
    fields = ('patient', 'city', 'center', 'doctor', 'visit_type', 'visit_date', 'status', 
              'chief_complaint', 'diagnosis', 'treatment_plan', 'notes', 'follow_up_date')
    
    # Enable actions for bulk operations
    actions = ['mark_as_scheduled', 'mark_as_in_progress', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_scheduled(self, request, queryset):
        """Mark selected visits as scheduled"""
        updated = queryset.update(status='SCHEDULED')
        self.message_user(request, f'{updated} visits marked as scheduled.')
    mark_as_scheduled.short_description = "Mark selected visits as scheduled"
    
    def mark_as_in_progress(self, request, queryset):
        """Mark selected visits as in progress"""
        updated = queryset.update(status='IN_PROGRESS')
        self.message_user(request, f'{updated} visits marked as in progress.')
    mark_as_in_progress.short_description = "Mark selected visits as in progress"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected visits as completed"""
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} visits marked as completed.')
    mark_as_completed.short_description = "Mark selected visits as completed"
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected visits as cancelled"""
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f'{updated} visits marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected visits as cancelled"
    
    
    def get_patient_name(self, obj):
        """Display patient name with styling"""
        if hasattr(obj.patient, 'patient_name') and obj.patient.patient_name:
            name = obj.patient.patient_name
        else:
            name = f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            name
        )
    get_patient_name.short_description = _('اسم المريض')
    
    def chief_complaint_short(self, obj):
        """Display shortened chief complaint"""
        if len(obj.chief_complaint) > 50:
            return f"{obj.chief_complaint[:50]}..."
        return obj.chief_complaint
    chief_complaint_short.short_description = _('الشكوى الرئيسية')
    
    def get_status_badge(self, obj):
        """Display status with colored badge"""
        status_colors = {
            'SCHEDULED': '#3b82f6',    # Blue
            'IN_PROGRESS': '#f59e0b',  # Orange
            'COMPLETED': '#10b981',    # Green
            'CANCELLED': '#ef4444',    # Red
            'NO_SHOW': '#6b7280',      # Gray
        }
        
        status_labels = {
            'SCHEDULED': 'مجدولة',
            'IN_PROGRESS': 'قيد التنفيذ',
            'COMPLETED': 'مكتملة',
            'CANCELLED': 'ملغية',
            'NO_SHOW': 'لم يحضر',
        }
        
        color = status_colors.get(obj.status, '#6b7280')
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">{}</span>',
            color, label
        )
    get_status_badge.short_description = _('الحالة')
    get_status_badge.admin_order_field = 'status'
    
    # Enhanced search with better performance
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            # Use select_related for better performance
            queryset = queryset.select_related('patient', 'patient__user', 'doctor', 'doctor__user')
            
            # Search in multiple fields
            from django.db.models import Q
            search_query = Q()
            
            # Search in patient name and ID
            search_query |= Q(patient__patient_name__icontains=search_term)
            search_query |= Q(patient__patient_id__icontains=search_term)
            
            # Search in doctor name
            search_query |= Q(doctor__user__first_name__icontains=search_term)
            search_query |= Q(doctor__user__last_name__icontains=search_term)
            
            # Search in chief complaint and diagnosis
            search_query |= Q(chief_complaint__icontains=search_term)
            search_query |= Q(diagnosis__icontains=search_term)
            search_query |= Q(treatment_plan__icontains=search_term)
            
            queryset = queryset.filter(search_query).distinct()
        
        return queryset, False
    
    def get_form(self, request, obj=None, **kwargs):
        """Return custom form with request context"""
        form_class = self.form
        
        class FormWithRequest(form_class):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)
        
        return FormWithRequest
    
    def add_view(self, request, form_url='', extra_context=None):
        """Override add_view to pass request to form"""
        print(f"🔍 [ADMIN VIEW] add_view called for user: {request.user}")
        print(f"🔍 [ADMIN VIEW] Request method: {request.method}")
        if request.method == 'POST':
            print(f"🔍 [ADMIN VIEW] POST data keys: {list(request.POST.keys())}")
            print(f"🔍 [ADMIN VIEW] POST data values:")
            for key, value in request.POST.items():
                print(f"    {key}: {value}")
        
        extra_context = extra_context or {}
        if request.user.role == 'ADMIN':
            extra_context['show_city_hospital'] = True
        return super().add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override change_view to pass request to form"""
        extra_context = extra_context or {}
        if request.user.role == 'ADMIN':
            extra_context['show_city_hospital'] = True
        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """Auto-assign user and handle role-based assignments"""
        if not change:  # Only for new patients
            # Create a new patient user instead of using admin user
            from apps.accounts.models import User
            
            # Get patient name from form data
            patient_name = form.cleaned_data.get('patient_name', '')
            if not patient_name:
                patient_name = f"Patient {obj.patient_id}"
            
            # Split name into first and last name
            name_parts = patient_name.strip().split(' ', 1)
            first_name = name_parts[0] if name_parts else 'Patient'
            last_name = name_parts[1] if len(name_parts) > 1 else obj.patient_id
            
            # Create new patient user
            patient_user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=f"patient_{obj.patient_id}@hospital.local",  # Temporary email
                role='PATIENT',
                is_active=True
            )
            
            # Set the patient user
            obj.user = patient_user
            
            # Auto-assign doctor based on role
            if request.user.role == 'DOCTOR':
                try:
                    obj.doctor = Doctor.objects.get(user=request.user)
                except Doctor.DoesNotExist:
                    # If doctor profile doesn't exist, this will be handled by form validation
                    pass
            elif request.user.role == 'STAFF' and hasattr(request.user, 'staff_profile'):
                # For staff, use the first doctor from their center if no doctor selected
                if not obj.doctor and request.user.staff_profile.center:
                    first_doctor = Doctor.objects.filter(center=request.user.staff_profile.center).first()
                    if first_doctor:
                        obj.doctor = first_doctor
        
        super().save_model(request, obj, form, change)
    
    
    def has_add_permission(self, request):
        """Control who can add patients"""
        return request.user.role in ['ADMIN', 'DOCTOR', 'STAFF']
    
    def has_change_permission(self, request, obj=None):
        """Control who can change patients"""
        if request.user.role == 'ADMIN':
            return True
        elif request.user.role == 'DOCTOR':
            return obj and obj.doctor.user == request.user
        elif request.user.role == 'STAFF':
            return obj and hasattr(request.user, 'staff_profile') and obj.doctor.center == request.user.staff_profile.center
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Control who can delete patients"""
        if request.user.role == 'ADMIN':
            return True
        elif request.user.role == 'DOCTOR':
            return obj and obj.doctor.user == request.user
        elif request.user.role == 'STAFF':
            return obj and hasattr(request.user, 'staff_profile') and obj.doctor.center == request.user.staff_profile.center
        return False
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _('إدارة المرضى - البحث والفلترة المتقدمة')
        
        # Add doctors list for filter sidebar based on role
        if request.user.role == 'ADMIN':
            extra_context['doctors'] = Doctor.objects.select_related('user', 'center').all()[:20]
        elif request.user.role == 'DOCTOR':
            extra_context['doctors'] = Doctor.objects.filter(user=request.user)
        elif request.user.role == 'STAFF' and hasattr(request.user, 'staff_profile'):
            extra_context['doctors'] = Doctor.objects.filter(center=request.user.staff_profile.center)
        
        # Add search statistics
        if request.GET.get('q'):
            search_term = request.GET.get('q')
            total_results = self.get_queryset(request).count()
            extra_context['search_info'] = f'تم العثور على {total_results} نتيجة للبحث عن "{search_term}"'
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_queryset(self, request):
        """Filter patients based on user role and optimize with select_related"""
        qs = super().get_queryset(request)
        
        if request.user.role == 'DOCTOR':
            # Doctors can only see their own patients
            qs = qs.filter(doctor__user=request.user)
        elif request.user.role == 'STAFF':
            # Staff can see patients from their center
            if hasattr(request.user, 'staff_profile') and request.user.staff_profile.center:
                qs = qs.filter(doctor__center=request.user.staff_profile.center)
            else:
                qs = qs.none()
        
        return qs.select_related('user', 'doctor', 'doctor__user')
    
    class Meta:
        verbose_name = _('المريض')
        verbose_name_plural = _('المرضى')


class PatientDiseaseForm(forms.ModelForm):
    """Custom form for PatientDisease with enhanced functionality"""
    
    class Meta:
        model = PatientDisease
        fields = '__all__'
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'disease': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'diagnosed_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'style': 'max-width: 200px !important;'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل ملاحظات إضافية'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request if provided
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Set Arabic labels
        self.fields['patient'].label = _('المريض')
        self.fields['disease'].label = _('المرض')
        self.fields['diagnosed_date'].label = _('تاريخ التشخيص')
        self.fields['status'].label = _('الحالة')
        self.fields['notes'].label = _('ملاحظات')
        
        # Set help texts
        self.fields['patient'].help_text = _('اختر المريض')
        self.fields['disease'].help_text = _('اختر المرض')
        self.fields['diagnosed_date'].help_text = _('تاريخ تشخيص المرض')
        self.fields['status'].help_text = _('حالة المرض الحالية')
        self.fields['notes'].help_text = _('ملاحظات إضافية حول المرض')
        
        # Set empty labels
        self.fields['patient'].empty_label = _('اختر المريض')
        self.fields['disease'].empty_label = _('اختر المرض')
        self.fields['status'].empty_label = _('اختر الحالة')


@admin.register(PatientDisease)
class PatientDiseaseAdmin(admin.ModelAdmin):
    form = PatientDiseaseForm
    list_display = ('get_patient_name', 'disease', 'diagnosed_date', 'get_status_badge', 'created_at')
    list_display_links = ('get_patient_name', 'disease')  # Make these clickable for editing
    list_filter = ('disease', 'status', 'diagnosed_date', 'created_at')
    search_fields = ('patient__patient_name', 'patient__patient_id', 'disease__name', 'notes')
    ordering = ('-diagnosed_date',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'diagnosed_date'
    preserve_filters = True
    list_select_related = ('patient', 'patient__user', 'disease')
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    # Enable actions for bulk operations
    actions = ['mark_as_active', 'mark_as_treated', 'mark_as_cured']
    
    def mark_as_active(self, request, queryset):
        """Mark selected diseases as active"""
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} diseases marked as active.')
    mark_as_active.short_description = "Mark selected diseases as active"
    
    def mark_as_treated(self, request, queryset):
        """Mark selected diseases as treated"""
        updated = queryset.update(status='TREATED')
        self.message_user(request, f'{updated} diseases marked as treated.')
    mark_as_treated.short_description = "Mark selected diseases as treated"
    
    def mark_as_cured(self, request, queryset):
        """Mark selected diseases as cured"""
        updated = queryset.update(status='CURED')
        self.message_user(request, f'{updated} diseases marked as cured.')
    mark_as_cured.short_description = "Mark selected diseases as cured"
    
    def get_form(self, request, obj=None, **kwargs):
        """Return custom form with related field widget for disease"""
        form_class = super().get_form(request, obj, **kwargs)
        
        class FormWithRelatedField(form_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Add related field widget for disease
                from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
                from django.urls import reverse
                
                # Only wrap if not already wrapped
                if not isinstance(self.fields['disease'].widget, RelatedFieldWidgetWrapper):
                    self.fields['disease'].widget = RelatedFieldWidgetWrapper(
                        self.fields['disease'].widget,
                        PatientDisease._meta.get_field('disease').remote_field,
                        admin_site=admin.site,
                        can_add_related=False,  # Disable add button
                        can_change_related=False,  # Disable change button
                        can_delete_related=False,
                        can_view_related=False,  # Disable view button
                    )
        
        return FormWithRelatedField
    
    fieldsets = (
        (_('معلومات التشخيص'), {
            'fields': ('patient', 'disease', 'diagnosed_date')
        }),
        (_('الحالة والملاحظات'), {
            'fields': ('status', 'notes')
        }),
    )
    
    def get_patient_name(self, obj):
        """Display patient name with styling"""
        if hasattr(obj.patient, 'patient_name') and obj.patient.patient_name:
            name = obj.patient.patient_name
        else:
            name = f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            name
        )
    get_patient_name.short_description = _('اسم المريض')
    
    def get_status_badge(self, obj):
        """Display status with colored badge"""
        status_colors = {
            'ACTIVE': '#ef4444',    # Red
            'TREATED': '#f59e0b',   # Orange
            'CHRONIC': '#8b5cf6',   # Purple
            'CURED': '#10b981',     # Green
        }
        
        status_labels = {
            'ACTIVE': 'نشط',
            'TREATED': 'معالج',
            'CHRONIC': 'مزمن',
            'CURED': 'مشفي',
        }
        
        color = status_colors.get(obj.status, '#6b7280')
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">{}</span>',
            color, label
        )
    get_status_badge.short_description = _('الحالة')
    get_status_badge.admin_order_field = 'status'
    
    # Enhanced search with better performance
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            # Use select_related for better performance
            queryset = queryset.select_related('patient', 'patient__user', 'disease')
            
            # Search in multiple fields
            from django.db.models import Q
            search_query = Q()
            
            # Search in patient name and ID
            search_query |= Q(patient__patient_name__icontains=search_term)
            search_query |= Q(patient__patient_id__icontains=search_term)
            
            # Search in disease name
            search_query |= Q(disease__name__icontains=search_term)
            
            # Search in notes
            search_query |= Q(notes__icontains=search_term)
            
            queryset = queryset.filter(search_query).distinct()
        
        return queryset, False


class TestListFilter(admin.SimpleListFilter):
    title = _('حالة الفحص')
    parameter_name = 'test_status'

    def lookups(self, request, model_admin):
        return (
            ('pending', _('معلق')),
            ('completed', _('مكتمل')),
            ('failed', _('فشل')),
            ('urgent', _('عاجل')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(status='PENDING')
        if self.value() == 'completed':
            return queryset.filter(status='COMPLETED')
        if self.value() == 'failed':
            return queryset.filter(status='CANCELLED')
        if self.value() == 'urgent':
            return queryset.filter(status='IN_PROGRESS')


class TestForm(forms.ModelForm):
    """Custom form for Test with enhanced functionality"""
    
    class Meta:
        model = Test
        fields = '__all__'
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'disease': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 300px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'test_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم الفحص'
            }),
            'test_type': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px !important; color: #000 !important; background-color: #fff !important;'
            }),
            'test_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'style': 'max-width: 200px !important;'
            }),
            'results': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل نتائج الفحص'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px !important; color: #000 !important; background-color: #fff !important;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract request if provided
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Set Arabic labels
        self.fields['patient'].label = _('المريض')
        self.fields['disease'].label = _('المرض')
        self.fields['test_name'].label = _('اسم الفحص')
        self.fields['test_type'].label = _('نوع الفحص')
        self.fields['test_date'].label = _('تاريخ الفحص')
        self.fields['results'].label = _('النتائج')
        self.fields['status'].label = _('الحالة')
        
        # Set help texts
        self.fields['patient'].help_text = _('اختر المريض')
        self.fields['disease'].help_text = _('اختر المرض')
        self.fields['test_name'].help_text = _('أدخل اسم الفحص')
        self.fields['test_type'].help_text = _('اختر نوع الفحص')
        self.fields['test_date'].help_text = _('تاريخ إجراء الفحص')
        self.fields['results'].help_text = _('أدخل نتائج الفحص')
        self.fields['status'].help_text = _('حالة الفحص الحالية')
        
        # Set empty labels
        self.fields['patient'].empty_label = _('اختر المريض')
        self.fields['disease'].empty_label = _('اختر المرض')
        self.fields['test_type'].empty_label = _('اختر نوع الفحص')
        self.fields['status'].empty_label = _('اختر الحالة')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    form = TestForm
    list_display = ('get_patient_name', 'disease', 'test_name', 'test_type', 'test_date', 'get_status_badge', 'created_at')
    list_display_links = ('get_patient_name', 'test_name')  # Make these clickable for editing
    list_filter = (TestListFilter, 'test_type', 'status', 'test_date', 'created_at')
    search_fields = ('patient__patient_name', 'patient__patient_id', 'test_name', 'disease__name', 'results')
    ordering = ('-test_date',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'test_date'
    preserve_filters = True
    list_select_related = ('patient', 'patient__user', 'disease')
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    # Enable actions for bulk operations
    actions = ['mark_as_pending', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_pending(self, request, queryset):
        """Mark selected tests as pending"""
        updated = queryset.update(status='PENDING')
        self.message_user(request, f'{updated} tests marked as pending.')
    mark_as_pending.short_description = "Mark selected tests as pending"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected tests as completed"""
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} tests marked as completed.')
    mark_as_completed.short_description = "Mark selected tests as completed"
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected tests as cancelled"""
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f'{updated} tests marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected tests as cancelled"
    
    def get_form(self, request, obj=None, **kwargs):
        """Return custom form with related field widget for disease"""
        form_class = super().get_form(request, obj, **kwargs)
        
        class FormWithRelatedField(form_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Add related field widget for disease
                from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
                
                # Only wrap if not already wrapped
                if not isinstance(self.fields['disease'].widget, RelatedFieldWidgetWrapper):
                    self.fields['disease'].widget = RelatedFieldWidgetWrapper(
                        self.fields['disease'].widget,
                        Test._meta.get_field('disease').remote_field,
                        admin_site=admin.site,
                        can_add_related=False,  # Disable add button
                        can_change_related=False,  # Disable change button
                        can_delete_related=False,
                        can_view_related=False,  # Disable view button
                    )
        
        return FormWithRelatedField
    
    fieldsets = (
        (_('معلومات الفحص'), {
            'fields': ('patient', 'disease', 'test_name', 'test_type')
        }),
        (_('التاريخ والنتائج'), {
            'fields': ('test_date', 'results', 'status')
        }),
    )
    
    def get_patient_name(self, obj):
        """Display patient name with styling"""
        if hasattr(obj.patient, 'patient_name') and obj.patient.patient_name:
            name = obj.patient.patient_name
        else:
            name = f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            name
        )
    get_patient_name.short_description = _('اسم المريض')
    
    def get_status_badge(self, obj):
        """Display status with colored badge"""
        status_colors = {
            'PENDING': '#f59e0b',    # Orange
            'COMPLETED': '#10b981',  # Green
            'CANCELLED': '#ef4444',  # Red
        }
        
        status_labels = {
            'PENDING': 'معلق',
            'COMPLETED': 'مكتمل',
            'CANCELLED': 'ملغي',
        }
        
        color = status_colors.get(obj.status, '#6b7280')
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">{}</span>',
            color, label
        )
    get_status_badge.short_description = _('الحالة')
    get_status_badge.admin_order_field = 'status'
    
    # Enhanced search with better performance
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            # Use select_related for better performance
            queryset = queryset.select_related('patient', 'patient__user', 'disease')
            
            # Search in multiple fields
            from django.db.models import Q
            search_query = Q()
            
            # Search in patient name and ID
            search_query |= Q(patient__patient_name__icontains=search_term)
            search_query |= Q(patient__patient_id__icontains=search_term)
            
            # Search in test name and results
            search_query |= Q(test_name__icontains=search_term)
            search_query |= Q(results__icontains=search_term)
            
            # Search in disease name
            search_query |= Q(disease__name__icontains=search_term)
            
            queryset = queryset.filter(search_query).distinct()
        
        return queryset, False
    
    def get_form(self, request, obj=None, **kwargs):
        """Return custom form with request context"""
        form_class = self.form
        
        class FormWithRequest(form_class):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)
        
        return FormWithRequest


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    """Admin configuration for Treatment model"""
    list_display = ['patient', 'disease', 'treatment_name', 'status', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'start_date', 'end_date', 'created_at', 'disease']
    search_fields = ['patient__patient_name', 'patient__patient_id', 'treatment_name', 'notes']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('معلومات العلاج'), {
            'fields': ('patient', 'disease', 'treatment_name', 'status')
        }),
        (_('التواريخ'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('التفاصيل'), {
            'fields': ('description', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        """Filter treatments based on user permissions"""
        qs = super().get_queryset(request)
        if request.user.role == 'DOCTOR':
            return qs.filter(patient__doctor__user=request.user)
        return qs


@admin.register(TreatmentMedicine)
class TreatmentMedicineAdmin(admin.ModelAdmin):
    """Admin configuration for TreatmentMedicine model"""
    list_display = ['treatment', 'medicine', 'dosage', 'frequency', 'duration_days']
    list_filter = ['medicine', 'frequency', 'duration_days']
    search_fields = ['treatment__patient__patient_name', 'medicine__name']
    ordering = ['treatment', 'medicine']
    
    fieldsets = (
        (_('العلاج والدواء'), {
            'fields': ('treatment', 'medicine')
        }),
        (_('الجرعة والاستخدام'), {
            'fields': ('dosage', 'frequency', 'duration_days', 'instructions')
        }),
    )


@admin.register(Surgery)
class SurgeryAdmin(admin.ModelAdmin):
    """Admin configuration for Surgery model"""
    list_display = ['patient', 'surgery_name', 'status', 'scheduled_date', 'surgeon_name', 'created_at']
    list_filter = ['status', 'scheduled_date', 'created_at', 'complications']
    search_fields = ['patient__patient_name', 'patient__patient_id', 'surgery_name', 'surgeon_name', 'notes']
    date_hierarchy = 'scheduled_date'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('معلومات العملية'), {
            'fields': ('patient', 'surgery_name', 'status', 'surgeon_name')
        }),
        (_('التواريخ'), {
            'fields': ('scheduled_date', 'actual_date')
        }),
        (_('التفاصيل'), {
            'fields': ('description', 'complications', 'complications_description', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        """Filter surgeries based on user permissions"""
        qs = super().get_queryset(request)
        if request.user.role == 'DOCTOR':
            return qs.filter(patient__doctor__user=request.user)
        return qs
