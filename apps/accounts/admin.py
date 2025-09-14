from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db import models
from django import forms
from .models import User


class UserCreationForm(forms.ModelForm):
    """Custom user creation form that handles username auto-generation"""
    
    password1 = forms.CharField(
        label=_('كلمة المرور'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label=_('تأكيد كلمة المرور'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'role')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("كلمات المرور غير متطابقة"))
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserListFilter(admin.SimpleListFilter):
    title = _('نوع المستخدم')
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        return (
            ('admin', _('مدير النظام')),
            ('doctor', _('طبيب')),
            ('staff', _('موظف')),
            ('patient', _('مريض')),
            ('verified', _('متحقق')),
            ('unverified', _('غير متحقق')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'admin':
            return queryset.filter(role='ADMIN')
        if self.value() == 'doctor':
            return queryset.filter(role='DOCTOR')
        if self.value() == 'staff':
            return queryset.filter(role='STAFF')
        if self.value() == 'patient':
            return queryset.filter(role='PATIENT')
        if self.value() == 'verified':
            return queryset.filter(is_verified=True)
        if self.value() == 'unverified':
            return queryset.filter(is_verified=False)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Arabic labels and professional display
    add_form = UserCreationForm
    list_display = ('email', 'get_full_name_ar', 'role_display', 'is_verified', 'is_active', 'created_at')
    list_filter = (UserListFilter, 'role', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    list_per_page = 25
    list_max_show_all = 100
    date_hierarchy = 'created_at'
    preserve_filters = True
    change_list_template = 'admin/change_list_universal.html'
    change_form_template = 'admin/change_form_universal.html'
    
    fieldsets = (
        (_('معلومات الدخول'), {'fields': ('email', 'password')}),
        (_('المعلومات الشخصية'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('الصلاحيات'), {'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('التواريخ المهمة'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    
    def get_full_name_ar(self, obj):
        """Display full name in Arabic format with styling"""
        name = f"{obj.first_name} {obj.last_name}"
        return format_html(
            '<span style="color: #1f2937; font-weight: 600;">{}</span>',
            name
        )
    get_full_name_ar.short_description = 'الاسم الكامل'
    
    def role_display(self, obj):
        """Display role in Arabic with styling"""
        role_names = {
            'ADMIN': 'مدير النظام',
            'DOCTOR': 'طبيب',
            'STAFF': 'موظف',
            'PATIENT': 'مريض',
        }
        role_name = role_names.get(obj.role, obj.role)
        role_colors = {
            'ADMIN': '#dc2626',
            'DOCTOR': '#059669',
            'STAFF': '#d97706',
            'PATIENT': '#2563eb',
        }
        color = role_colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: 600; background: {}20; padding: 2px 8px; border-radius: 12px;">{}</span>',
            color, color, role_name
        )
    role_display.short_description = 'الدور'
    
    def get_queryset(self, request):
        """Filter users based on role"""
        qs = super().get_queryset(request)
        if request.user.role == 'DOCTOR':
            # Doctors can only see patients and their own profile
            return qs.filter(role__in=['PATIENT', 'DOCTOR']).filter(
                models.Q(role='PATIENT') | models.Q(id=request.user.id)
            )
        elif request.user.role == 'STAFF':
            # Staff can see patients and staff
            return qs.filter(role__in=['PATIENT', 'STAFF'])
        return qs
    
    def has_add_permission(self, request):
        """Control who can add users"""
        if request.user.role == 'ADMIN':
            return True
        elif request.user.role == 'DOCTOR':
            return False  # Doctors can't add users
        elif request.user.role == 'STAFF':
            return False  # Staff can't add users
        return False
    
    def has_change_permission(self, request, obj=None):
        """Control who can change users"""
        if request.user.role == 'ADMIN':
            return True
        elif request.user.role == 'DOCTOR':
            return obj and obj.id == request.user.id  # Only their own profile
        elif request.user.role == 'STAFF':
            return obj and obj.role in ['PATIENT', 'STAFF']  # Only patients and staff
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Control who can delete users"""
        return request.user.role == 'ADMIN'
