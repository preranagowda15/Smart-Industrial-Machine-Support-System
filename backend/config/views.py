"""
backend/config/views.py - Serves the HTML frontend templates
"""

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie
import os


def index_view(request):
    if not request.user.is_authenticated:
        return redirect('page-login')
    role = getattr(request.user, 'role', 'OPERATOR')
    if role == 'ADMIN':
        return redirect('page-admin-dashboard')
    if role == 'SUPERVISOR':
        return redirect('page-review-queue')
    return redirect('page-upload')


@ensure_csrf_cookie
def login_view(request):
    return render(request, 'login.html')


@ensure_csrf_cookie
def register_view(request):
    return render(request, 'register.html')


@ensure_csrf_cookie
def upload_view(request):
    return render(request, 'upload.html')


@ensure_csrf_cookie
def history_view(request):
    return render(request, 'history.html')


@ensure_csrf_cookie
def review_queue_view(request):
    return render(request, 'review_queue.html')


@ensure_csrf_cookie
def evaluation_view(request):
    return render(request, 'evaluation.html')


@ensure_csrf_cookie
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')


@ensure_csrf_cookie
def inspection_detail_page_view(request, id):
    return render(request, 'inspection_detail.html', {'inspection_id': id})


def serve_project_file(request, path):
    """
    Serves Samples/ and Validation/ files for the frontend test buttons.
    """
    safe_path = os.path.normpath(path).lstrip(os.sep)
    allowed_prefixes = ('Samples', 'Validation')
    if not any(safe_path.startswith(prefix) for prefix in allowed_prefixes):
        raise Http404("File not found.")

    full_path = os.path.join(settings.BASE_DIR, safe_path)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise Http404("File not found on disk.")

    return FileResponse(open(full_path, 'rb'))
