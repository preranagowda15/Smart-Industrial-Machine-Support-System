"""
Root URL Configuration for Plate Inspection System
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    index_view,
    login_view,
    register_view,
    upload_view,
    history_view,
    review_queue_view,
    evaluation_view,
    admin_dashboard_view,
    inspection_detail_page_view,
    serve_project_file,
)

urlpatterns = [
    # Administrative console
    path('admin/', admin.site.urls),

    # REST APIs
    path('api/auth/', include('apps.accounts.urls')),
    path('api/inspections/', include('apps.inspections.urls')),
    path('api/evaluation/', include('apps.evaluation.urls')),
    path('api/model/', include('apps.evaluation.integrity_urls')),
    path('api/users/', include('apps.accounts.user_urls')),

    # Frontend UI Pages
    path('', index_view, name='page-index'),
    path('login/', login_view, name='page-login'),
    path('register/', register_view, name='page-register'),
    path('dashboard/', upload_view, name='page-dashboard-alias'),
    path('engineer-dashboard/', upload_view, name='page-engineer-alias'),
    path('upload/', upload_view, name='page-upload'),
    path('history/', history_view, name='page-history'),
    path('review-queue/', review_queue_view, name='page-review-queue'),
    path('evaluation/', evaluation_view, name='page-evaluation'),
    path('admin-dashboard/', admin_dashboard_view, name='page-admin-dashboard'),
    path('inspections/<int:id>/', inspection_detail_page_view, name='page-inspection-detail'),

    # Test Fixtures Serving (Samples/ and Validation/)
    re_path(r'^(?P<path>(Samples|Validation)/.*)$', serve_project_file, name='serve-fixture'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
