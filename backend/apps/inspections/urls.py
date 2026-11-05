from django.urls import path, include
from .views import InspectionListCreateView, InspectionDetailView

urlpatterns = [
    path('', InspectionListCreateView.as_view(), name='inspection-list-create'),
    path('<int:pk>/', InspectionDetailView.as_view(), name='inspection-detail'),
    path('<int:pk>/reviews/', include('apps.reviews.urls')),
]
