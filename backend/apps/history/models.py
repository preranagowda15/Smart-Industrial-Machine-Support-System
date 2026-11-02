from django.db import models
from django.conf import settings
from backend.apps.machines.models import Machine
from backend.apps.manuals.models import Manual, DocumentChunk

class QuestionHistory(models.Model):
    class Status(models.TextChoices):
        ANSWERED = "ANSWERED", "Answered"
        INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE", "Insufficient Evidence"
        PROCESSING = "PROCESSING", "Processing"
        ERROR = "ERROR", "Processing Error"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions")
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT, related_name="questions")
    question = models.TextField()
    answer = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PROCESSING,
        db_index=True
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    retrieved_sources = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "Question histories"

    def __str__(self):
        return f"[{self.status}] {self.machine.machine_code}: {self.question[:40]}..."

class SourceReference(models.Model):
    question_history = models.ForeignKey(
        QuestionHistory,
        on_delete=models.CASCADE,
        related_name="source_references"
    )
    manual = models.ForeignKey(
        Manual,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="references"
    )
    chunk = models.ForeignKey(
        DocumentChunk,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="references"
    )
    document_name = models.CharField(max_length=100)
    revision = models.CharField(max_length=30, default="1.0")
    pdf_page = models.PositiveIntegerField(help_text="1-based physical PDF page number")
    passage_text = models.TextField()
    pdf_url = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["document_name", "pdf_page"]

    def __str__(self):
        return f"{self.document_name} p.{self.pdf_page}"

