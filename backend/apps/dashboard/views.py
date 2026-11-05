from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.db.models import Count, Q
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.accounts.permissions import role_of, IsSupervisor, IsAdministrator
from apps.machines.models import Machine
from apps.manuals.models import Manual, DocumentChunk
from apps.history.models import QuestionHistory
from apps.history.serializers import QuestionHistorySerializer

# ========================================================
# REST APIs for Supervisor Dashboard
# ========================================================

class SupervisorQuestionsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]

    def get(self, request):
        qs = QuestionHistory.objects.all().select_related("user", "machine").prefetch_related("source_references")
        machine_code = request.query_params.get("machine_code")
        if machine_code:
            qs = qs.filter(machine__machine_code=machine_code)
        return Response(QuestionHistorySerializer(qs[:200], many=True).data)

class SupervisorUnansweredAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]

    def get(self, request):
        qs = QuestionHistory.objects.filter(
            status__in=[QuestionHistory.Status.INSUFFICIENT_EVIDENCE, QuestionHistory.Status.ERROR]
        ).select_related("user", "machine").prefetch_related("source_references")
        return Response(QuestionHistorySerializer(qs[:100], many=True).data)

class SupervisorMetricsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]

    def get(self, request):
        total_questions = QuestionHistory.objects.count()
        answered = QuestionHistory.objects.filter(status=QuestionHistory.Status.ANSWERED).count()
        insufficient = QuestionHistory.objects.filter(status=QuestionHistory.Status.INSUFFICIENT_EVIDENCE).count()
        errors = QuestionHistory.objects.filter(status=QuestionHistory.Status.ERROR).count()

        by_machine = (
            QuestionHistory.objects.values("machine__machine_code", "machine__machine_name")
            .annotate(
                total=Count("id"),
                answered=Count("id", filter=Q(status=QuestionHistory.Status.ANSWERED)),
                insufficient=Count("id", filter=Q(status=QuestionHistory.Status.INSUFFICIENT_EVIDENCE))
            )
            .order_by("-total")
        )

        return Response({
            "metrics": {
                "total_questions": total_questions,
                "answered_questions": answered,
                "insufficient_evidence_questions": insufficient,
                "error_questions": errors,
                "answer_rate_percent": round((answered / total_questions * 100), 1) if total_questions > 0 else 0.0,
            },
            "by_machine": list(by_machine),
            "total_machines": Machine.objects.filter(is_active=True).count(),
            "total_manuals": Manual.objects.count(),
        })

# ========================================================
# Frontend Page Template Views
# ========================================================

def login_page(request):
    if request.user.is_authenticated:
        role = role_of(request.user)
        if role == "ADMIN":
            return redirect("page-admin-dashboard")
        if role == "SUPERVISOR":
            return redirect("page-review-queue")
        return redirect("page-upload")
    return render(request, "login.html")

def register_page(request):
    if request.user.is_authenticated:
        return redirect("page-upload")
    return render(request, "register.html")

def logout_view(request):
    logout(request)
    return redirect("page-login")

def dashboard_home(request):
    return redirect("page-upload")

def engineer_dashboard_page(request):
    role = role_of(request.user) if request.user.is_authenticated else "ENGINEER"
    machines = Machine.objects.filter(is_active=True).prefetch_related("manuals")
    my_history = QuestionHistory.objects.filter(user=request.user) if request.user.is_authenticated else QuestionHistory.objects.none()
    
    total_my_questions = my_history.count()
    answered_count = my_history.filter(status=QuestionHistory.Status.ANSWERED).count()
    insufficient_count = my_history.filter(status=QuestionHistory.Status.INSUFFICIENT_EVIDENCE).count()
    grounding_rate = round((answered_count / total_my_questions * 100), 1) if total_my_questions > 0 else 100.0

    return render(request, "engineer_dashboard.html", {
        "user_role": role,
        "machines": machines,
        "recent_questions": my_history[:6],
        "total_my_questions": total_my_questions,
        "answered_count": answered_count,
        "insufficient_count": insufficient_count,
        "grounding_rate": grounding_rate,
        "page_title": "Engineer Dashboard",
    })

@ensure_csrf_cookie
def assistant_page(request):
    role = role_of(request.user) if request.user.is_authenticated else "ENGINEER"
    machines = Machine.objects.filter(is_active=True)
    return render(request, "assistant.html", {
        "user_role": role,
        "machines": machines,
        "page_title": "AI Maintenance Assistant"
    })

@ensure_csrf_cookie
def manuals_page(request):
    role = role_of(request.user) if request.user.is_authenticated else "ADMIN"
    machines = Machine.objects.filter(is_active=True)
    manuals = Manual.objects.all().select_related("machine")
    return render(request, "manuals.html", {
        "user_role": role,
        "machines": machines,
        "manuals": manuals,
        "page_title": "Machine Manuals"
    })

@ensure_csrf_cookie
def history_page(request):
    role = role_of(request.user) if request.user.is_authenticated else "ENGINEER"
    machines = Machine.objects.filter(is_active=True)
    return render(request, "question_history.html", {
        "user_role": role,
        "machines": machines,
        "page_title": "Maintenance Question History"
    })

@ensure_csrf_cookie
def supervisor_dashboard_page(request):
    role = role_of(request.user) if request.user.is_authenticated else "SUPERVISOR"
    machines = Machine.objects.filter(is_active=True)
    return render(request, "supervisor_dashboard.html", {
        "user_role": role,
        "machines": machines,
        "page_title": "Supervisor Audit Overview"
    })

@ensure_csrf_cookie
def admin_dashboard_page(request):
    role = role_of(request.user) if request.user.is_authenticated else "ADMIN"
    machines = Machine.objects.all().prefetch_related("manuals")
    manuals = Manual.objects.all().select_related("machine")
    users = User.objects.all().order_by("-date_joined")
    total_chunks = DocumentChunk.objects.count()
    return render(request, "admin_dashboard.html", {
        "user_role": role,
        "machines": machines,
        "manuals": manuals,
        "users": users,
        "total_users": users.count(),
        "total_chunks": total_chunks,
        "page_title": "Administrator Control"
    })
