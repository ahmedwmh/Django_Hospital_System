import os

# Check if Celery is available
try:
    from celery import Celery
    
    # Set default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
    
    app = Celery('hospital_system')
    
    # Using a string here means the worker doesn't have to serialize
    # the configuration object to child processes.
    app.config_from_object('django.conf:settings', namespace='CELERY')
    
    # Load task modules from all registered Django apps.
    app.autodiscover_tasks()
    
    @app.task(bind=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')
        
except ImportError:
    # Celery not available, create a dummy app
    app = None
