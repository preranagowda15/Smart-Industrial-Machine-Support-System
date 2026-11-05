from django.urls import path
from .views import ModelIntegrityView

urlpatterns = [
    path('integrity/', ModelIntegrityView.as_view(), name='model-integrity'),
]
