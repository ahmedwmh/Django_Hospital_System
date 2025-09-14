from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'patient-diseases', views.PatientDiseaseViewSet)
router.register(r'tests', views.TestViewSet)
router.register(r'treatments', views.TreatmentViewSet)
router.register(r'surgeries', views.SurgeryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # AJAX endpoints for admin form filtering
    path('admin/get-centers-by-city/', views.get_centers_by_city, name='get_centers_by_city'),
    path('admin/get-doctors-by-center/', views.get_doctors_by_center, name='get_doctors_by_center'),
    path('check-phone-uniqueness/', views.check_phone_uniqueness, name='check_phone_uniqueness'),
    # Patient profile page
    path('admin/patient-profile/<int:patient_id>/', views.patient_profile, name='patient_profile'),
]
