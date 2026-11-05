"""
backend/apps/evaluation/models.py - Evaluation Run Record
"""

from django.db import models
from django.conf import settings


class EvaluationRun(models.Model):
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluation_runs'
    )
    total_samples = models.IntegerField(default=0)
    successful_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    tp = models.IntegerField(default=0)
    fn = models.IntegerField(default=0)
    fp = models.IntegerField(default=0)
    tn = models.IntegerField(default=0)
    defect_recall = models.FloatField(default=0.0)
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    fn_zero_caveat = models.TextField(blank=True, null=True)
    model_version = models.CharField(max_length=64, default='BIT-PLATE-CV-1.0')
    raw_report = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Evaluation Run #{self.id} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')}) - Recall: {self.defect_recall}"
