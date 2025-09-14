from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import User


class RoleBasedUserAdmin(BaseUserAdmin):
    """Custom User Admin with Arabic labels and role-based access"""
    
    # Arabic labels
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'created_at')
    list_filter = ('role', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    
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


# Register the custom admin
admin.site.unregister(User)
admin.site.register(User, RoleBasedUserAdmin)
