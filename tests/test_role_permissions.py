import io
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from backend.apps.accounts.models import User
from backend.apps.machines.models import Machine
from backend.apps.manuals.models import Manual

class RolePermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Users for each role
        self.engineer = User.objects.create_user(
            username="test_engineer",
            password="EngineerPassword123!",
            role=User.Role.ENGINEER
        )
        self.supervisor = User.objects.create_user(
            username="test_supervisor",
            password="SupervisorPassword123!",
            role=User.Role.SUPERVISOR
        )
        self.admin = User.objects.create_user(
            username="test_admin",
            password="AdminPassword123!",
            role=User.Role.ADMIN,
            is_staff=True
        )

        self.machine = Machine.objects.create(
            machine_code="M-HP200",
            machine_name="HP-200 Hydraulic Press",
            is_active=True
        )

    def test_mandatory_1_engineer_upload_denial(self):
        """
        MANDATORY TEST 1: ENGINEER UPLOAD DENIAL
        - Create Engineer user.
        - Authenticate.
        - Attempt POST /api/manuals/upload/.
        - Verify HTTP 403 Forbidden.
        - Verify no manual was created.
        """
        self.client.force_authenticate(user=self.engineer)
        initial_count = Manual.objects.count()

        fake_pdf = SimpleUploadedFile(
            "unauthorized_manual.pdf",
            b"%PDF-1.4 Fake PDF Content",
            content_type="application/pdf"
        )
        response = self.client.post(
            "/api/manuals/upload/",
            {
                "machine_id": self.machine.machine_code,
                "document_name": "HP-UNAUTH-01",
                "revision": "1.0",
                "pdf_file": fake_pdf,
            },
            format="multipart"
        )

        self.assertEqual(
            response.status_code, 403,
            f"Expected HTTP 403 Forbidden for Engineer upload, got {response.status_code}"
        )
        self.assertEqual(
            Manual.objects.count(), initial_count,
            "No manual record should be created when Engineer attempts upload."
        )

    def test_supervisor_cannot_upload_manual(self):
        """Supervisors should also be prevented from uploading manuals (Admin only)."""
        self.client.force_authenticate(user=self.supervisor)
        fake_pdf = SimpleUploadedFile("sup_test.pdf", b"%PDF-1.4", content_type="application/pdf")
        response = self.client.post("/api/manuals/upload/", {"machine_id": self.machine.id, "pdf_file": fake_pdf}, format="multipart")
        self.assertEqual(response.status_code, 403)

    def test_engineer_cannot_access_supervisor_metrics(self):
        """Engineers must receive 403 when trying to access supervisor metrics."""
        self.client.force_authenticate(user=self.engineer)
        response = self.client.get("/api/supervisor/metrics/")
        self.assertEqual(response.status_code, 403)

    def test_supervisor_can_access_supervisor_metrics(self):
        """Supervisors can successfully access supervisor metrics."""
        self.client.force_authenticate(user=self.supervisor)
        response = self.client.get("/api/supervisor/metrics/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("metrics", response.data)

    def test_unauthenticated_requests_denied(self):
        """Unauthenticated requests to protected endpoints return 401."""
        response = self.client.get("/api/machines/")
        self.assertEqual(response.status_code, 401)
