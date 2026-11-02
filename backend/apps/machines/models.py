from django.db import models

class Machine(models.Model):
    machine_code = models.CharField(max_length=50, unique=True, db_index=True)
    machine_name = models.CharField(max_length=150)
    manufacturer = models.CharField(max_length=150, blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["machine_code"]

    def __str__(self):
        return f"{self.machine_code} — {self.machine_name}"

