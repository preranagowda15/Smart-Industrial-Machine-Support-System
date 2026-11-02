from django.urls import path
from .views import ManualListAPIView, ManualDetailAPIView, ManualStatusAPIView, ManualUploadAPIView

urlpatterns = [
    path("", ManualListAPIView.as_view(), name="manual-list"),
    path("upload/", ManualUploadAPIView.as_view(), name="manual-upload"),
    path("<int:pk>/", ManualDetailAPIView.as_view(), name="manual-detail"),
    path("<int:pk>/status/", ManualStatusAPIView.as_view(), name="manual-status"),
]
