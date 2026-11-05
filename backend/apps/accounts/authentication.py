from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication subclass that disables CSRF enforcement for API endpoints.
    Allows JWT API endpoints and AJAX calls to function without CSRF token failures.
    """
    def enforce_csrf(self, request):
        return  # CSRF check skipped for API requests

