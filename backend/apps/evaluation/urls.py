from django.urls import path
from .views import EvaluationLatestView, EvaluationRunView

urlpatterns = [
    path('', EvaluationLatestView.as_view(), name='evaluation-latest'),
    path('run/', EvaluationRunView.as_view(), name='evaluation-run'),
]
