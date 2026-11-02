from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginAPIView, LogoutAPIView, CurrentUserAPIView, UserListCreateAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="auth-login"),
    path("logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("me/", CurrentUserAPIView.as_view(), name="auth-me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("users/", UserListCreateAPIView.as_view(), name="auth-users"),
]
