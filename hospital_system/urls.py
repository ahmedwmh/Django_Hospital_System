"""
URL configuration for hospital_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.patients.views import patient_profile

# Import admin config to ensure custom admin site is registered
from hospital_system import admin_config

def redirect_to_admin(request):
    return redirect('/admin/')

urlpatterns = [
    path('', redirect_to_admin, name='home'),
    path('health/', include('apps.health.urls')),
    
    # Direct patient profile access - MUST come before admin URLs
    path('admin/patients/patient-profile/<int:patient_id>/', patient_profile, name='admin_patient_profile'),
    
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/hospital/', include('apps.hospital.urls')),
    path('api/v1/patients/', include('apps.patients.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve static and media files in production (needed for DigitalOcean App Platform)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
