from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from backend.apps.accounts.models import User
from backend.apps.machines.models import Machine
from backend.apps.history.models import QuestionHistory
from backend.services.rag_service import INSUFFICIENT_EVIDENCE_TEXT

class EndToEndScenariosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.engineer = User.objects.create_user(
            username="e2e_engineer", password="EngineerPass123!", role=User.Role.ENGINEER
        )
        cls.supervisor = User.objects.create_user(
            username="e2e_supervisor", password="SupervisorPass123!", role=User.Role.SUPERVISOR
        )
        cls.admin = User.objects.create_user(
            username="e2e_admin", password="AdminPass123!", role=User.Role.ADMIN, is_staff=True
        )

        # Create Machines
        cls.hp200 = Machine.objects.create(
            machine_code="M-HP200", machine_name="HP-200 Hydraulic Forming Press", is_active=True
        )
        cls.ac90 = Machine.objects.create(
            machine_code="M-AC90", machine_name="AC-90 Rotary Screw Compressor", is_active=True
        )

    def setUp(self):
        self.client = APIClient()

    def test_scenario_1_supported_question(self):
        """
        SCENARIO 1 — SUPPORTED QUESTION
        Machine: HP-200
        Question: 'What does E17 mean?'
        Expected:
        - Retrieve relevant HP-200 passage.
        - Generate evidence-grounded answer.
        - Display document and revision.
        - Display exact PDF page.
        - Open cited page URL.
        """
        self.client.force_authenticate(user=self.engineer)
        response = self.client.post(
            "/api/assistant/ask/",
            {"machine_id": "M-HP200", "question": "What does E17 mean?"},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["status"], "ANSWERED")
        self.assertIn("Main Ram Proportional Valve", data["answer"])
        self.assertTrue(len(data["source_references"]) > 0)
        
        source = data["source_references"][0]
        self.assertEqual(source["document_name"], "HP-OPS-01")
        self.assertEqual(source["pdf_page"], 2)
        self.assertIn("#page=2", source["pdf_url"])

    def test_scenario_2_multi_document_question(self):
        """
        SCENARIO 2 — MULTI-DOCUMENT QUESTION
        Machine: HP-200
        Question: 'What should be inspected during maintenance, and what operating limits should be checked?'
        Expected:
        - Retrieve from both HP-200 manuals.
        - Combine evidence.
        - Cite both documents.
        """
        self.client.force_authenticate(user=self.engineer)
        response = self.client.post(
            "/api/assistant/ask/",
            {
                "machine_id": "M-HP200",
                "question": "What should be inspected during maintenance, and what operating limits should be checked?"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["status"], "ANSWERED")
        
        cited_docs = {s["document_name"] for s in data["source_references"]}
        self.assertIn("HP-OPS-01", cited_docs)
        self.assertIn("HP-MNT-01", cited_docs)

    def test_scenario_3_machine_isolation(self):
        """
        SCENARIO 3 — MACHINE ISOLATION
        Select HP-200.
        Ask: AC-90 rated discharge pressure question.
        Expected:
        - No AC-90 passages retrieved.
        - Insufficient-evidence response.
        - No fabricated answer.
        """
        self.client.force_authenticate(user=self.engineer)
        response = self.client.post(
            "/api/assistant/ask/",
            {"machine_id": "M-HP200", "question": "What is the AC-90 rated discharge pressure?"},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(data["answer"], INSUFFICIENT_EVIDENCE_TEXT)
        self.assertEqual(len(data["source_references"]), 0)

    def test_scenario_4_unsupported_question(self):
        """
        SCENARIO 4 — UNSUPPORTED QUESTION
        Ask a question that neither machine manual answers.
        Expected:
        - Insufficient-evidence response.
        - No external knowledge.
        - Persisted question history.
        - Visible in supervisor dashboard.
        """
        self.client.force_authenticate(user=self.engineer)
        response = self.client.post(
            "/api/assistant/ask/",
            {"machine_id": "M-HP200", "question": "What is the supplier replacement price for the hydraulic pump?"},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(data["answer"], INSUFFICIENT_EVIDENCE_TEXT)

        # Check persisted in database
        persisted = QuestionHistory.objects.filter(pk=data["id"]).first()
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted.status, "INSUFFICIENT_EVIDENCE")

        # Check visible in supervisor dashboard
        self.client.force_authenticate(user=self.supervisor)
        sup_response = self.client.get("/api/supervisor/unanswered/")
        self.assertEqual(sup_response.status_code, 200)
        unanswered_ids = [item["id"] for item in sup_response.data]
        self.assertIn(persisted.id, unanswered_ids)

    def test_scenario_5_role_security(self):
        """
        SCENARIO 5 — ROLE SECURITY
        Log in as Engineer.
        Attempt to upload manual.
        Expected:
        - Backend returns 403.
        - Upload is denied.
        - No document is stored.
        Log in as Supervisor and verify question history is accessible.
        """
        # Engineer upload attempt
        self.client.force_authenticate(user=self.engineer)
        fake_pdf = SimpleUploadedFile("malicious.pdf", b"%PDF-1.4 Fake", content_type="application/pdf")
        upload_resp = self.client.post(
            "/api/manuals/upload/",
            {"machine_id": "M-HP200", "document_name": "HP-EXPLOIT", "pdf_file": fake_pdf},
            format="multipart"
        )
        self.assertEqual(upload_resp.status_code, 403)

        # Supervisor question history check
        self.client.force_authenticate(user=self.supervisor)
        hist_resp = self.client.get("/api/supervisor/questions/")
        self.assertEqual(hist_resp.status_code, 200)
        self.assertIsInstance(hist_resp.data, list)
