from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('test/', views.simple_test, name='simple_test'),
]
