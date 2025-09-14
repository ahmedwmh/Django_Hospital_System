from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import AdminSite


class HospitalAdminSite(AdminSite):
    """Custom Admin Site for Hospital Management System with Arabic support"""
    
    site_header = _('نظام إدارة المستشفى')
    site_title = _('إدارة المستشفى')
    index_title = _('لوحة التحكم الرئيسية')
    
    def get_app_list(self, request):
        """Customize app list based on user role"""
        app_list = super().get_app_list(request)
        
        if request.user.role == 'ADMIN':
            # Super Admin sees everything
            return app_list
        elif request.user.role == 'DOCTOR':
            # Doctor sees limited apps
            allowed_apps = ['accounts', 'patients', 'hospital']
            return [app for app in app_list if app['app_label'] in allowed_apps]
        elif request.user.role == 'STAFF':
            # Staff sees limited apps
            allowed_apps = ['accounts', 'patients']
            return [app for app in app_list if app['app_label'] in allowed_apps]
        elif request.user.role == 'PATIENT':
            # Patients see only their own data
            return []
        
        return app_list
    
    def index(self, request, extra_context=None):
        """Custom index page with role-based content"""
        extra_context = extra_context or {}
        
        # Add role-specific context
        extra_context.update({
            'user_role': request.user.role,
            'role_display': self.get_role_display(request.user.role),
        })
        
        # Add dashboard statistics
        try:
            from apps.accounts.models import User
            from apps.hospital.models import Center, Doctor
            from apps.patients.models import Patient
            
            # Get actual counts
            total_users = User.objects.count()
            total_centers = Center.objects.count()
            total_doctors = Doctor.objects.count()
            total_patients = Patient.objects.count()
            
            # Debug: Print counts to console
            print(f"Dashboard counts - Users: {total_users}, Centers: {total_centers}, Doctors: {total_doctors}, Patients: {total_patients}")
            
            extra_context.update({
                'total_users': total_users,
                'total_centers': total_centers,
                'total_doctors': total_doctors,
                'total_patients': total_patients,
            })
        except Exception as e:
            # If models are not available, set defaults
            print(f"Error getting dashboard counts: {e}")
            extra_context.update({
                'total_users': 0,
                'total_centers': 0,
                'total_doctors': 0,
                'total_patients': 0,
            })
        
        return super().index(request, extra_context)
    
    def get_role_display(self, role):
        """Get Arabic display name for role"""
        role_names = {
            'ADMIN': 'مدير النظام',
            'DOCTOR': 'طبيب',
            'STAFF': 'موظف',
            'PATIENT': 'مريض',
        }
        return role_names.get(role, role)


# Modify the existing admin site instead of creating a new one
admin.site.site_header = 'نظام إدارة المستشفى'
admin.site.site_title = 'إدارة المستشفى'
admin.site.index_title = 'لوحة التحكم الرئيسية'

# Add our custom index method to the existing admin site
original_index = admin.site.index

def custom_index(request, extra_context=None):
    """Custom index method with dashboard statistics"""
    if extra_context is None:
        extra_context = {}
    
    # Add user role information
    extra_context.update({
        'user_role': request.user.role,
        'role_display': get_role_display(request.user.role),
    })
    
    # Add dashboard statistics
    try:
        from apps.accounts.models import User
        from apps.hospital.models import Center, Doctor
        from apps.patients.models import Patient
        
        # Get actual counts
        total_users = User.objects.count()
        total_centers = Center.objects.count()
        total_doctors = Doctor.objects.count()
        total_patients = Patient.objects.count()
        
        # Debug: Print counts to console
        print(f"Dashboard counts - Users: {total_users}, Centers: {total_centers}, Doctors: {total_doctors}, Patients: {total_patients}")
        
        extra_context.update({
            'total_users': total_users,
            'total_centers': total_centers,
            'total_doctors': total_doctors,
            'total_patients': total_patients,
        })
    except Exception as e:
        # If models are not available, set defaults
        print(f"Error getting dashboard counts: {e}")
        extra_context.update({
            'total_users': 0,
            'total_centers': 0,
            'total_doctors': 0,
            'total_patients': 0,
        })
    
    return original_index(request, extra_context)

def get_role_display(role):
    """Get Arabic display name for role"""
    role_names = {
        'ADMIN': 'مدير النظام',
        'DOCTOR': 'طبيب',
        'STAFF': 'موظف',
        'PATIENT': 'مريض',
    }
    return role_names.get(role, role)

# Replace the index method
admin.site.index = custom_index

# Add custom CSS for Arabic support
from django.template.loader import get_template
from django.template import Context

def add_arabic_css():
    """Add Arabic CSS to admin templates"""
    from django.contrib.admin.views.main import ChangeList
    from django.contrib.admin.views.decorators import staff_member_required
    from django.utils.decorators import method_decorator
    from django.shortcuts import render
    
    # This will be handled in the template
    pass
