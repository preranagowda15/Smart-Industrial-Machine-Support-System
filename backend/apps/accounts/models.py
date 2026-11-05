from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        OPERATOR = 'OPERATOR', 'Operator'
        ENGINEER = 'ENGINEER', 'Engineer'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OPERATOR,
        help_text="User system role for permission enforcement."
    )

    def is_operator(self):
        return self.role in (self.Role.OPERATOR, self.Role.ENGINEER)

    def is_engineer_role(self):
        return self.role in (self.Role.ENGINEER, self.Role.OPERATOR)

    def is_supervisor(self):
        return self.role == self.Role.SUPERVISOR

    def is_supervisor_role(self):
        return self.role == self.Role.SUPERVISOR

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def save(self, *args, **kwargs):
        # Sync superuser status with ADMIN role
        if self.is_superuser:
            self.role = self.Role.ADMIN
        elif self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"

