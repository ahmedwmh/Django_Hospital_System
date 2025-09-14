from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class HospitalAdminSite(AdminSite):
    """Custom Admin Site for Hospital Management System"""
    
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


# Create custom admin site instance
hospital_admin_site = HospitalAdminSite(name='hospital_admin')
