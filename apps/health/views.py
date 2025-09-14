from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json
import os


@csrf_exempt
def health_check(request):
    """Health check endpoint for Digital Ocean App Platform"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "OK"
    except Exception as e:
        db_status = f"ERROR: {str(e)}"
    
    health_data = {
        "status": "healthy",
        "database": db_status,
        "app": "Django Hospital System",
        "version": "1.0.0",
        "debug": os.environ.get('DEBUG', 'False'),
        "allowed_hosts": os.environ.get('ALLOWED_HOSTS', 'Not set'),
        "port": os.environ.get('PORT', 'Not set')
    }
    
    return JsonResponse(health_data)


@csrf_exempt
def simple_test(request):
    """Simple test endpoint"""
    return HttpResponse("Hello! Django Hospital System is working!", content_type="text/plain")
