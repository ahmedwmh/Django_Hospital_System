from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cities', views.CityViewSet)
router.register(r'centers', views.CenterViewSet)
router.register(r'doctors', views.DoctorViewSet)
router.register(r'staff', views.StaffViewSet)
router.register(r'medicines', views.MedicineViewSet)
router.register(r'diseases', views.DiseaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('centers-by-city/', views.centers_by_city, name='centers_by_city'),
]
