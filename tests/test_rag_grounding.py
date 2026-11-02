from django.test import TestCase
from backend.services.rag_service import RAGService, INSUFFICIENT_EVIDENCE_TEXT
from backend.services.retrieval_service import RetrievalService
from backend.services.citation_service import CitationService
from backend.services.pdf_processor import PDFProcessor

class RAGGroundingTests(TestCase):
    def setUp(self):
        self.rag = RAGService()

    def test_e17_grounded_answer_and_citation(self):
        """Supported question E17 returns grounded answer citing HP-OPS-01 page 2."""
        res = self.rag.ask("What does E17 mean?", machine_code="M-HP200", machine_name="HP-200")
        self.assertEqual(res["evidence_status"], "ANSWERED")
        self.assertIn("Main Ram Proportional Valve", res["answer"])
        self.assertTrue(len(res["citations"]) > 0)
        citation = res["citations"][0]
        self.assertEqual(citation["document_id"], "HP-OPS-01")
        self.assertEqual(citation["pdf_page"], 2)
        self.assertIn("#page=2", citation["pdf_url"])

    def test_cross_machine_question_returns_insufficient_evidence(self):
        """Selecting HP-200 and asking an AC-90 question returns INSUFFICIENT_EVIDENCE."""
        res = self.rag.ask("What is the AC-90 rated discharge pressure?", machine_code="M-HP200", machine_name="HP-200")
        self.assertEqual(res["evidence_status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(res["answer"], INSUFFICIENT_EVIDENCE_TEXT)
        self.assertEqual(len(res["citations"]), 0)

    def test_unsupported_topic_returns_insufficient_evidence(self):
        """Asking about pricing or CNC lathes returns INSUFFICIENT_EVIDENCE."""
        res = self.rag.ask("What is the pump replacement price from the supplier?", machine_code="M-HP200", machine_name="HP-200")
        self.assertEqual(res["evidence_status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(res["answer"], INSUFFICIENT_EVIDENCE_TEXT)
        self.assertEqual(len(res["citations"]), 0)

    def test_citation_validation_rejects_hallucinations(self):
        """CitationService rejects out-of-bounds indices and mismatched machine codes."""
        fake_hits = [
            {"text": "Sample text", "metadata": {"machine_id": "M-HP200", "document_id": "HP-OPS-01", "page_number": 1}}
        ]
        # Claim index 99 (out of range) and mismatched machine
        citations = CitationService.validate_and_format_citations(
            claimed_indices=[1, 99],
            retrieved_hits=fake_hits,
            expected_machine_code="M-AC90"  # Expecting AC-90, but hit is HP-200
        )
        self.assertEqual(len(citations), 0, "Mismatched machine hit must be rejected")
