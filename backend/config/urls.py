from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # REST APIs
    path("api/auth/", include("backend.apps.accounts.urls")),
    path("api/machines/", include("backend.apps.machines.urls")),
    path("api/manuals/", include("backend.apps.manuals.urls")),
    path("api/assistant/history/", include("backend.apps.history.urls")),
    path("api/assistant/", include("backend.apps.assistant.urls")),

    # Frontend Views and Supervisor APIs
    path("", include("backend.apps.dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

