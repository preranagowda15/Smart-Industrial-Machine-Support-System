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


def role_of(user) -> str:
    if not user or not user.is_authenticated:
        return "ANONYMOUS"
    if getattr(user, "is_superuser", False):
        return "ADMIN"
    return str(getattr(user, "role", "OPERATOR")).upper()


class IsSupervisor(permissions.BasePermission):
    message = "Supervisor access required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role in [User.Role.SUPERVISOR, User.Role.ADMIN] or request.user.is_superuser))


class IsAdministrator(permissions.BasePermission):
    message = "Administrator access required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == User.Role.ADMIN or request.user.is_superuser))


class IsEngineer(permissions.BasePermission):
    message = "Engineer access required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in [User.Role.ENGINEER, User.Role.OPERATOR, User.Role.ADMIN])



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


def role_of(user) -> str:
    if not user or not user.is_authenticated:
        return "ANONYMOUS"
    if getattr(user, "is_superuser", False):
        return "ADMIN"
    return str(getattr(user, "role", "OPERATOR")).upper()


class IsSupervisor(permissions.BasePermission):
    message = "Supervisor access required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role in [User.Role.SUPERVISOR, User.Role.ADMIN] or request.user.is_superuser))


class IsAdministrator(permissions.BasePermission):
    message = "Administrator access required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == User.Role.ADMIN or request.user.is_superuser))


class IsEngineer(permissions.BasePermission):
    message = "Engineer access required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in [User.Role.ENGINEER, User.Role.OPERATOR, User.Role.ADMIN])


