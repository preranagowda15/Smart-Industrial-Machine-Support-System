"""
backend/apps/inspections/models.py - Inspection Model with Immutability
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Inspection(models.Model):
    class Status(models.TextChoices):
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    class PredictionClass(models.IntegerChoices):
        NORMAL = 0, 'Normal'
        DEFECTIVE = 1, 'Defective'

    LIMITATIONS_NOTICE = (
        "Demonstration system for product P-PLATE01 on synthetic images. "
        "Confidence score is an uncalibrated model score, not a probability of safety. "
        "Evaluates binary Normal/Defective status only, without defect location, severity, or cause. "
        "Independent human review is required."
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inspections'
    )
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255, blank=True)

    # Model inference fields
    predicted_class = models.IntegerField(
        choices=PredictionClass.choices,
        null=True,
        blank=True,
        help_text="0 for Normal, 1 for Defective"
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Uncalibrated probability score of the predicted class (0.0 to 1.0)"
    )
    defect_probability = models.FloatField(
        null=True,
        blank=True,
        help_text="Uncalibrated defect probability score (0.0 to 1.0)"
    )
    model_version = models.CharField(
        max_length=64,
        blank=True,
        help_text="Version identifier of the model that generated this prediction"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED
    )
    error_message = models.TextField(blank=True)

    # Retry lineage (Section 6.3: Retry creates a NEW inspection attempt linked to original)
    parent_inspection = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='retries'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def predicted_label(self):
        if self.predicted_class == 0:
            return "Normal"
        elif self.predicted_class == 1:
            return "Defective"
        return "Unknown"

    def clean(self):
        """
        Enforce Section 6.3 Immutability:
        The original prediction fields are never updated after completion.
        """
        if self.pk:
            orig = Inspection.objects.filter(pk=self.pk).first()
            if orig and orig.status == self.Status.COMPLETED:
                immutable_fields = [
                    'predicted_class',
                    'confidence',
                    'defect_probability',
                    'model_version',
                    'image'
                ]
                for field in immutable_fields:
                    if getattr(self, field) != getattr(orig, field):
                        raise ValidationError(
                            f"Inspection prediction is immutable and cannot be updated after completion. "
                            f"Attempted to modify: {field}"
                        )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Inspection #{self.id} - {self.predicted_label} ({self.status}) by {self.user.username}"
