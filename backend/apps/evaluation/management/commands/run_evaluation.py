"""
Management command: run_evaluation
Executes model evaluation on all 60 sample images in Samples/labels.csv.
"""

from django.core.management.base import BaseCommand
from services.metrics_service import evaluate_samples
from apps.evaluation.models import EvaluationRun


class Command(BaseCommand):
    help = "Run model evaluation on all 60 labeled sample images."

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-save',
            action='store_true',
            help='Do not save evaluation run record to the database.'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Running model evaluation on Samples/labels.csv..."))
        report = evaluate_samples()

        if not options['no_save']:
            EvaluationRun.objects.create(
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

        self.stdout.write("\n" + "="*60)
        self.stdout.write(f"BIT-PLATE-CV-1.0 EVALUATION REPORT")
        self.stdout.write(f"Model Version: {report['model_version']}")
        self.stdout.write(f"Timestamp:     {report['evaluated_at']}")
        self.stdout.write(f"Total Samples: {report['total_samples']}")
        self.stdout.write(f"Successful:    {report['successful_count']}")
        self.stdout.write(f"Failed:        {report['failed_count']}")
        self.stdout.write("="*60)

        # 2x2 Confusion Matrix Table
        # Rows = actual (Normal, Defective), Columns = predicted (Normal, Defective)
        cm = report['confusion_matrix']
        self.stdout.write("\n2x2 CONFUSION MATRIX (rows = actual, columns = predicted):")
        self.stdout.write("------------------------------------------------------------")
        self.stdout.write(f"{'':<20} | {'Pred Normal (0)':<18} | {'Pred Defective (1)':<18}")
        self.stdout.write("------------------------------------------------------------")
        self.stdout.write(f"{'Actual Normal (0)':<20} | {cm[0][0]:<18} (TN) | {cm[0][1]:<18} (FP)")
        self.stdout.write(f"{'Actual Defective (1)':<20} | {cm[1][0]:<18} (FN) | {cm[1][1]:<18} (TP)")
        self.stdout.write("------------------------------------------------------------\n")

        # Primary and Secondary Metrics
        self.stdout.write(self.style.SUCCESS(f"Defect Recall (TP / (TP+FN)):  {report['defect_recall'] * 100:.2f}%"))
        self.stdout.write(f"Overall Accuracy:              {report['accuracy'] * 100:.2f}%")
        self.stdout.write(f"Precision:                     {report['precision'] * 100:.2f}%\n")

        # Missing / Failed files explicitly
        if report['failed_count'] > 0:
            self.stdout.write(self.style.WARNING("FAILED / MISSING PREDICTIONS:"))
            for f_item in report['failed_predictions']:
                self.stdout.write(f"  - Path: {f_item['path']} | Actual: {f_item['actual_name']} | Error: {f_item['error']}")
            self.stdout.write("")

        # FN = 0 Caveat Statement
        if report['fn_zero_caveat']:
            self.stdout.write(self.style.WARNING("="*60))
            self.stdout.write(self.style.WARNING("LIMITATION STATEMENT:"))
            self.stdout.write(self.style.WARNING(report['fn_zero_caveat']))
            self.stdout.write(self.style.WARNING("="*60))

        self.stdout.write(self.style.SUCCESS("\nEvaluation completed successfully.\n"))

