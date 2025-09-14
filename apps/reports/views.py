from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from .models import Report
from .serializers import ReportSerializer
from .tasks import generate_patient_record_pdf, generate_test_results_pdf, generate_treatment_summary_pdf, generate_surgery_report_pdf, generate_patients_per_city_excel, generate_common_diseases_excel
from apps.patients.models import Patient
from apps.hospital.permissions import IsAdminOrReadOnly


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reports
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        """
        Filter reports based on user role
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        else:
            return self.queryset.filter(generated_by=user)
    
    @action(detail=False, methods=['post'])
    def generate_patient_record(self, request):
        """Generate patient record PDF"""
        patient_id = request.data.get('patient_id')
        if not patient_id:
            return Response({'error': 'patient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create report record
        report = Report.objects.create(
            name=f"Patient Record - {patient.user.get_full_name()}",
            report_type='PATIENT_RECORD',
            format='PDF',
            generated_by=request.user,
            parameters={'patient_id': patient_id}
        )
        
        # Start background task
        generate_patient_record_pdf.delay(report.id)
        
        return Response({
            'message': 'Report generation started',
            'report_id': report.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'])
    def generate_test_results(self, request):
        """Generate test results PDF"""
        patient_id = request.data.get('patient_id')
        test_ids = request.data.get('test_ids', [])
        
        if not patient_id:
            return Response({'error': 'patient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create report record
        report = Report.objects.create(
            name=f"Test Results - {patient.user.get_full_name()}",
            report_type='TEST_RESULTS',
            format='PDF',
            generated_by=request.user,
            parameters={'patient_id': patient_id, 'test_ids': test_ids}
        )
        
        # Start background task
        generate_test_results_pdf.delay(report.id)
        
        return Response({
            'message': 'Report generation started',
            'report_id': report.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'])
    def generate_treatment_summary(self, request):
        """Generate treatment summary PDF"""
        patient_id = request.data.get('patient_id')
        treatment_ids = request.data.get('treatment_ids', [])
        
        if not patient_id:
            return Response({'error': 'patient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create report record
        report = Report.objects.create(
            name=f"Treatment Summary - {patient.user.get_full_name()}",
            report_type='TREATMENT_SUMMARY',
            format='PDF',
            generated_by=request.user,
            parameters={'patient_id': patient_id, 'treatment_ids': treatment_ids}
        )
        
        # Start background task
        generate_treatment_summary_pdf.delay(report.id)
        
        return Response({
            'message': 'Report generation started',
            'report_id': report.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'])
    def generate_surgery_report(self, request):
        """Generate surgery report PDF"""
        surgery_id = request.data.get('surgery_id')
        
        if not surgery_id:
            return Response({'error': 'surgery_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apps.patients.models import Surgery
            surgery = Surgery.objects.get(id=surgery_id)
        except Surgery.DoesNotExist:
            return Response({'error': 'Surgery not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create report record
        report = Report.objects.create(
            name=f"Surgery Report - {surgery.surgery_name}",
            report_type='SURGERY_REPORT',
            format='PDF',
            generated_by=request.user,
            parameters={'surgery_id': surgery_id}
        )
        
        # Start background task
        generate_surgery_report_pdf.delay(report.id)
        
        return Response({
            'message': 'Report generation started',
            'report_id': report.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'])
    def generate_patients_per_city(self, request):
        """Generate patients per city Excel report"""
        city_ids = request.data.get('city_ids', [])
        
        # Create report record
        report = Report.objects.create(
            name="Patients per City Report",
            report_type='PATIENTS_PER_CITY',
            format='EXCEL',
            generated_by=request.user,
            parameters={'city_ids': city_ids}
        )
        
        # Start background task
        generate_patients_per_city_excel.delay(report.id)
        
        return Response({
            'message': 'Report generation started',
            'report_id': report.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'])
    def generate_common_diseases(self, request):
        """Generate common diseases Excel report"""
        center_ids = request.data.get('center_ids', [])
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        # Create report record
        report = Report.objects.create(
            name="Common Diseases Report",
            report_type='COMMON_DISEASES',
            format='EXCEL',
            generated_by=request.user,
            parameters={
                'center_ids': center_ids,
                'start_date': start_date,
                'end_date': end_date
            }
        )
        
        # Start background task
        generate_common_diseases_excel.delay(report.id)
        
        return Response({
            'message': 'Report generation started',
            'report_id': report.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download generated report"""
        report = self.get_object()
        
        if report.status != 'COMPLETED':
            return Response({'error': 'Report not ready'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not report.file_path:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            import os
            if os.path.exists(report.file_path):
                response = FileResponse(
                    open(report.file_path, 'rb'),
                    as_attachment=True,
                    filename=f"{report.name}.{report.format.lower()}"
                )
                return response
            else:
                return Response({'error': 'File not found on server'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
