from django.urls import path
from .views import QuestionHistoryListAPIView, QuestionHistoryDetailAPIView

urlpatterns = [
    path("", QuestionHistoryListAPIView.as_view(), name="history-list"),
    path("<int:pk>/", QuestionHistoryDetailAPIView.as_view(), name="history-detail"),
]
