"""
backend/config/views.py - Serves the HTML frontend templates
"""

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import FileResponse, Http404
import os


def index_view(request):
    return redirect('page-upload')


def login_view(request):
    return render(request, 'login.html')


def register_view(request):
    return render(request, 'register.html')


def upload_view(request):
    return render(request, 'upload.html')


def history_view(request):
    return render(request, 'history.html')


def review_queue_view(request):
    return render(request, 'review_queue.html')


def evaluation_view(request):
    return render(request, 'evaluation.html')


def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')


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

