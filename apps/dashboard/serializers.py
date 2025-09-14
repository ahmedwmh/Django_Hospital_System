from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_users = serializers.IntegerField()
    total_patients = serializers.IntegerField()
    total_doctors = serializers.IntegerField()
    total_staff = serializers.IntegerField()
    total_centers = serializers.IntegerField()
    total_cities = serializers.IntegerField()
    total_diseases = serializers.IntegerField()
    total_medicines = serializers.IntegerField()
    active_patients = serializers.IntegerField()
    available_doctors = serializers.IntegerField()
    active_staff = serializers.IntegerField()
    active_centers = serializers.IntegerField()
