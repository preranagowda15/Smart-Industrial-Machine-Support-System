from django.db import models
from django.conf import settings
from apps.machines.models import Machine

class Manual(models.Model):
    class IngestionStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="manuals")
    document_name = models.CharField(max_length=100, unique=True)
    revision = models.CharField(max_length=30, default="1.0")
    pdf_file = models.FileField(upload_to="manuals/")
    total_pages = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_manuals"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ingestion_status = models.CharField(
        max_length=20,
        choices=IngestionStatus.choices,
        default=IngestionStatus.PENDING
    )
    error_message = models.TextField(blank=True, default="")

    class Meta:
        app_label = "manuals"
        ordering = ["machine__machine_code", "document_name"]

    def __str__(self):
        return f"{self.document_name} Rev {self.revision} ({self.machine.machine_code})"

class DocumentChunk(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="chunks")
    manual = models.ForeignKey(Manual, on_delete=models.CASCADE, related_name="chunks")
    chunk_text = models.TextField()
    page_number = models.PositiveIntegerField(help_text="1-based physical PDF page number")
    chunk_index = models.PositiveIntegerField()
    embedding_id = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "manuals"
        ordering = ["manual", "page_number", "chunk_index"]

    def __str__(self):
        return f"{self.manual.document_name} p.{self.page_number} c.{self.chunk_index}"

