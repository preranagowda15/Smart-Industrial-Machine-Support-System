from django.urls import path
from .views import MachineListCreateAPIView, MachineDetailAPIView

urlpatterns = [
    path("", MachineListCreateAPIView.as_view(), name="machine-list-create"),
    path("<int:pk>/", MachineDetailAPIView.as_view(), name="machine-detail"),
]
