"""
backend/apps/reviews/models.py - Append-only Review model
Enforces Section 6.3:
Supervisor reviews go in a separate append-only Review table (reviewer, decision CONFIRMED/OVERRIDDEN, comment, timestamp).
Never delete or edit reviews.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Review(models.Model):
    class Decision(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        OVERRIDDEN = 'OVERRIDDEN', 'Overridden'

    inspection = models.ForeignKey(
        'inspections.Inspection',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    decision = models.CharField(
        max_length=20,
        choices=Decision.choices
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def clean(self):
        # Prevent any edits to existing reviews (append-only)
        if self.pk:
            orig = Review.objects.filter(pk=self.pk).first()
            if orig:
                raise ValidationError("Reviews are append-only and cannot be modified after submission.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Reviews are permanent audit records and cannot be deleted.")

    def __str__(self):
        return f"Review #{self.id} on Inspection #{self.inspection_id}: {self.decision} by {self.reviewer.username}"
