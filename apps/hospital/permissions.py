from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions only for admins
        return request.user.is_authenticated and request.user.is_admin


class IsDoctorOrAdmin(BasePermission):
    """
    Custom permission to only allow doctors and admins to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_doctor or request.user.is_admin)


class IsStaffOrAdmin(BasePermission):
    """
    Custom permission to only allow staff and admins to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_admin)


class IsPatientOrDoctorOrAdmin(BasePermission):
    """
    Custom permission to allow patients, doctors, and admins to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_patient or 
            request.user.is_doctor or 
            request.user.is_admin
        )


class IsOwnerOrDoctorOrAdmin(BasePermission):
    """
    Custom permission to only allow owners, doctors, and admins to access.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.is_admin:
            return True
        
        # Doctor can access their patients' data
        if request.user.is_doctor and hasattr(obj, 'patient'):
            return obj.patient.doctor.user == request.user
        
        # Patient can access their own data
        if request.user.is_patient and hasattr(obj, 'patient'):
            return obj.patient.user == request.user
        
        # For user objects, check if it's the same user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
