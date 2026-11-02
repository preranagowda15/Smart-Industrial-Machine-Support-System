from django.urls import path
from .views import AskAssistantAPIView

urlpatterns = [
    path("ask/", AskAssistantAPIView.as_view(), name="assistant-ask"),
]
