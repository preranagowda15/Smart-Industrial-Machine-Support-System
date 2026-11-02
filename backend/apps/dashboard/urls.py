from django.urls import path
from .views import (
    SupervisorQuestionsAPIView,
    SupervisorUnansweredAPIView,
    SupervisorMetricsAPIView,
    login_page,
    logout_view,
    dashboard_home,
    assistant_page,
    manuals_page,
    history_page,
    supervisor_dashboard_page,
    admin_dashboard_page,
)

urlpatterns = [
    # REST API for supervisor
    path("api/supervisor/questions/", SupervisorQuestionsAPIView.as_view(), name="api-supervisor-questions"),
    path("api/supervisor/unanswered/", SupervisorUnansweredAPIView.as_view(), name="api-supervisor-unanswered"),
    path("api/supervisor/metrics/", SupervisorMetricsAPIView.as_view(), name="api-supervisor-metrics"),

    # Page Routes
    path("", dashboard_home, name="dashboard-home"),
    path("login/", login_page, name="login"),
    path("logout/", logout_view, name="logout"),
    path("assistant/", assistant_page, name="assistant-page"),
    path("manuals/", manuals_page, name="manuals-page"),
    path("history/", history_page, name="history-page"),
    path("supervisor/", supervisor_dashboard_page, name="supervisor-dashboard"),
    path("admin-panel/", admin_dashboard_page, name="admin-dashboard"),
]
