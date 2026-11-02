from rest_framework.permissions import BasePermission

def role_of(user) -> str:
    """Returns the role string of the user (or 'ANONYMOUS')."""
    if not user or not user.is_authenticated:
        return "ANONYMOUS"
    if getattr(user, "is_superuser", False) or getattr(user, "role", "") == "ADMIN":
        return "ADMIN"
    return getattr(user, "role", "ENGINEER")

class IsAdministrator(BasePermission):
    """Allows access only to users with the Administrator role."""
    message = "Access denied: Only Administrators have permission to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == "ADMIN" or request.user.is_superuser)
        )

class IsEngineer(BasePermission):
    """Allows access to Engineers and Administrators."""
    message = "Access denied: Only Engineers can use the AI Assistant."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ("ENGINEER", "ADMIN")
        )

class IsSupervisor(BasePermission):
    """Allows access to Supervisors and Administrators."""
    message = "Access denied: Only Supervisors and Administrators can access supervisor logs and metrics."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ("SUPERVISOR", "ADMIN") or
            getattr(request.user, "is_superuser", False)
        )

