from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import EvaluationRun
from apps.accounts.permissions import IsSupervisorOrAdmin, IsAdminRole
from services.metrics_service import evaluate_samples
from services.integrity_service import verify_integrity


class EvaluationLatestView(APIView):
    """
    GET /api/evaluation/
    Returns the latest evaluation report. If none exists, executes a fresh evaluation.
    Allowed for Supervisor and Admin.
    """
    permission_classes = [permissions.IsAuthenticated, IsSupervisorOrAdmin]

    def get(self, request):
        latest = EvaluationRun.objects.first()
        if not latest:
            # Generate initial run
            report = evaluate_samples()
            latest = EvaluationRun.objects.create(
                executed_by=request.user,
                total_samples=report['total_samples'],
                successful_count=report['successful_count'],
                failed_count=report['failed_count'],
                tp=report['tp'],
                fn=report['fn'],
                fp=report['fp'],
                tn=report['tn'],
                defect_recall=report['defect_recall'],
                accuracy=report['accuracy'],
                precision=report['precision'],
                fn_zero_caveat=report['fn_zero_caveat'],
                model_version=report['model_version'],
                raw_report=report
            )
            return Response(report, status=status.HTTP_200_OK)

        return Response(latest.raw_report, status=status.HTTP_200_OK)


class EvaluationRunView(APIView):
    """
    POST /api/evaluation/run/
    Executes a fresh evaluation run on all 60 sample images.
    Allowed for Supervisor and Admin.
    """
    permission_classes = [permissions.IsAuthenticated, IsSupervisorOrAdmin]

    def post(self, request):
        report = evaluate_samples()
        run = EvaluationRun.objects.create(
            executed_by=request.user,
            total_samples=report['total_samples'],
            successful_count=report['successful_count'],
            failed_count=report['failed_count'],
            tp=report['tp'],
            fn=report['fn'],
            fp=report['fp'],
            tn=report['tn'],
            defect_recall=report['defect_recall'],
            accuracy=report['accuracy'],
            precision=report['precision'],
            fn_zero_caveat=report['fn_zero_caveat'],
            model_version=report['model_version'],
            raw_report=report
        )
        return Response(report, status=status.HTTP_201_CREATED)


class ModelIntegrityView(APIView):
    """
    GET /api/model/integrity/
    Verifies SHA256 checksums of all model and dataset files.
    Admin only.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        result = verify_integrity()
        status_code = status.HTTP_200_OK if result['is_valid'] else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(result, status=status_code)

