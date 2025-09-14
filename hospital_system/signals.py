from django.apps import AppConfig
from django.contrib import admin
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def re_register_admin_models(sender, **kwargs):
    """Re-register all admin models with the custom admin site after migrations"""
    if sender.name == 'hospital_system':
        # Import all admin modules to ensure they're registered
        from apps.accounts import admin as accounts_admin
        from apps.hospital import admin as hospital_admin
        from apps.patients import admin as patients_admin
        from apps.reports import admin as reports_admin
        
        # The models should now be registered with our custom admin site
        print("Admin models re-registered with custom admin site")
