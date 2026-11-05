"""
Batch inference processor for AI visual quality inspections.
Processes image inspection batches asynchronously, tracking per-item status.
Ensures an invalid item does not halt valid batch items.
"""
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from django.utils import timezone
from apps.inspections.models import Inspection, InspectionBatch
from apps.inspections.services.image_validator import ImageValidator, ImageValidationError
from apps.inspections.services.classifier_service import ClassifierService

_executor = ThreadPoolExecutor(max_workers=3)

class BatchProcessor:
    @staticmethod
    def process_inspection_item(inspection_id: str):
        """Processes a single inspection item."""
        try:
            inspection = Inspection.objects.get(pk=inspection_id)
        except Inspection.DoesNotExist:
            return

        inspection.status = Inspection.Status.PROCESSING
        inspection.save(update_fields=["status"])

        try:
            # If the item already has a failure reason from upload, mark as FAILED
            if inspection.failure_reason:
                inspection.status = Inspection.Status.FAILED
                inspection.save(update_fields=["status"])
                BatchProcessor._update_batch_progress(inspection.batch)
                return

            if not inspection.image_file or not os.path.exists(inspection.image_file.path):
                inspection.status = Inspection.Status.FAILED
                inspection.failure_reason = "Image file not found on disk."
                inspection.save(update_fields=["status", "failure_reason"])
                BatchProcessor._update_batch_progress(inspection.batch)
                return

            # Validate image content
            with open(inspection.image_file.path, "rb") as f:
                val = ImageValidator.validate_file(f, filename=inspection.filename)
            
            inspection.image_width = val["width"]
            inspection.image_height = val["height"]
            inspection.file_size_bytes = val["size_bytes"]

            # Run CV model prediction
            res = ClassifierService.run_inference(inspection.image_file.path)
            inspection.predicted_class = res["predicted_class"]
            inspection.confidence = res["confidence"]
            inspection.defect_probability = res["defect_probability"]
            inspection.model_version = res["model_version"]
            inspection.status = Inspection.Status.COMPLETED
            inspection.save(update_fields=[
                "image_width", "image_height", "file_size_bytes",
                "predicted_class", "confidence", "defect_probability",
                "model_version", "status"
            ])

        except ImageValidationError as ve:
            inspection.status = Inspection.Status.FAILED
            inspection.failure_reason = str(ve)
            inspection.save(update_fields=["status", "failure_reason"])
        except Exception as e:
            inspection.status = Inspection.Status.FAILED
            inspection.failure_reason = f"Inference processing error: {str(e)}"
            inspection.save(update_fields=["status", "failure_reason"])
        finally:
            BatchProcessor._update_batch_progress(inspection.batch)

    @staticmethod
    def _update_batch_progress(batch: InspectionBatch):
        if not batch:
            return

        total = batch.items.count()
        completed = batch.items.filter(status=Inspection.Status.COMPLETED).count()
        failed = batch.items.filter(status=Inspection.Status.FAILED).count()
        queued_or_processing = batch.items.filter(
            status__in=[Inspection.Status.QUEUED, Inspection.Status.PROCESSING]
        ).count()

        batch.total_items = total
        batch.completed_items = completed
        batch.failed_items = failed

        if queued_or_processing == 0:
            if failed == 0:
                batch.status = InspectionBatch.Status.COMPLETED
            elif completed > 0:
                batch.status = InspectionBatch.Status.PARTIAL_FAILURE
            else:
                batch.status = InspectionBatch.Status.FAILED
        else:
            batch.status = InspectionBatch.Status.PROCESSING

        batch.save(update_fields=["total_items", "completed_items", "failed_items", "status"])

    @staticmethod
    def queue_batch(batch_id: str):
        """Asynchronously dispatches all items in a batch to the thread worker."""
        def run():
            try:
                batch = InspectionBatch.objects.get(pk=batch_id)
                batch.status = InspectionBatch.Status.PROCESSING
                batch.save(update_fields=["status"])
                item_ids = list(batch.items.values_list("id", flat=True))
                for item_id in item_ids:
                    BatchProcessor.process_inspection_item(item_id)
            except Exception as e:
                print(f"[BatchProcessor] Error processing batch {batch_id}: {e}")

        _executor.submit(run)

