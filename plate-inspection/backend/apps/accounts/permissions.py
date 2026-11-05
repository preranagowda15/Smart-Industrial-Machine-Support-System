from rest_framework import permissions
from .models import User


class IsSupervisorOrAdmin(permissions.BasePermission):
    """
    Allows access only to Supervisors or Admins.
    """
    message = "Supervisor or Admin role required to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.role in [User.Role.SUPERVISOR, User.Role.ADMIN] or
            request.user.is_superuser
        )


class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to Admin users.
    """
    message = "Administrator role required to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.role == User.Role.ADMIN or
            request.user.is_superuser
        )


class CanReviewInspection(permissions.BasePermission):
    """
    Explicit permission check for review actions: Operators are forbidden (403).
    """
    message = "Operators are not permitted to review or override inspections."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.role in [User.Role.SUPERVISOR, User.Role.ADMIN] or
            request.user.is_superuser
        )

