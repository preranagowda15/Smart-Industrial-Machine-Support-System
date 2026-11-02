from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.apps.accounts.permissions import role_of, IsSupervisor, IsAdministrator
from backend.apps.machines.models import Machine
from backend.apps.manuals.models import Manual
from backend.apps.history.models import QuestionHistory
from backend.apps.history.serializers import QuestionHistorySerializer

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
        return redirect("dashboard-home")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard_home(request):
    role = role_of(request.user)
    if role == "ADMIN":
        return redirect("admin-dashboard")
    elif role == "SUPERVISOR":
        return redirect("supervisor-dashboard")
    else:
        return redirect("assistant-page")

@login_required
def assistant_page(request):
    role = role_of(request.user)
    machines = Machine.objects.filter(is_active=True)
    return render(request, "assistant.html", {
        "user_role": role,
        "machines": machines,
        "page_title": "AI Assistant"
    })

@login_required
def manuals_page(request):
    role = role_of(request.user)
    machines = Machine.objects.filter(is_active=True)
    manuals = Manual.objects.all().select_related("machine")
    return render(request, "manuals.html", {
        "user_role": role,
        "machines": machines,
        "manuals": manuals,
        "page_title": "Machine Manuals"
    })

@login_required
def history_page(request):
    role = role_of(request.user)
    machines = Machine.objects.filter(is_active=True)
    return render(request, "history.html", {
        "user_role": role,
        "machines": machines,
        "page_title": "Question History"
    })

@login_required
def supervisor_dashboard_page(request):
    role = role_of(request.user)
    if role not in ("SUPERVISOR", "ADMIN"):
        return redirect("assistant-page")
    machines = Machine.objects.filter(is_active=True)
    return render(request, "supervisor_dashboard.html", {
        "user_role": role,
        "machines": machines,
        "page_title": "Supervisor Overview"
    })

@login_required
def admin_dashboard_page(request):
    role = role_of(request.user)
    if role != "ADMIN":
        return redirect("dashboard-home")
    machines = Machine.objects.all()
    manuals = Manual.objects.all().select_related("machine")
    return render(request, "admin_dashboard.html", {
        "user_role": role,
        "machines": machines,
        "manuals": manuals,
        "page_title": "Administrator Control"
    })
