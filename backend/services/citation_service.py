"""
Citation validation and PDF navigation service.
Validates citations against actual retrieved source chunks, ensures no hallucinated
page numbers, and constructs working /media/manuals/<pdf>#page=<page> viewer URLs.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import pymupdf

DOC_PDF_MAP = {
    "HP-OPS-01": "HP200_Operations_Rev1_0.pdf",
    "HP-MNT-01": "HP200_Maintenance_Rev1_0.pdf",
    "AC-OM-01": "AC90_Operations_Maintenance_Rev1_0.pdf",
}

class CitationService:
    @staticmethod
    def calculate_line_range(doc_id: str, page_no: int, passage: str) -> str:
        """Calculates 1-based start and end line numbers of the passage on the PDF page."""
        try:
            filename = DOC_PDF_MAP.get(doc_id)
            if not filename:
                return ""
            for base in [Path("data/Manuals"), Path("media/manuals")]:
                pdf_path = base / filename
                if pdf_path.exists():
                    doc = pymupdf.open(str(pdf_path))
                    if 0 <= page_no - 1 < len(doc):
                        page = doc[page_no - 1]
                        lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
                        doc.close()
                        words = [w.lower().strip(".,;:!?\"'()[]{}") for w in passage.split() if len(w) > 3]
                        if not words or not lines:
                            return ""
                        start_line = 1
                        end_line = len(lines)
                        for idx, l in enumerate(lines, 1):
                            if any(w in l.lower() for w in words[:3]):
                                start_line = idx
                                break
                        for idx in range(len(lines), 0, -1):
                            l = lines[idx - 1]
                            if any(w in l.lower() for w in words[-3:]):
                                end_line = idx
                                break
                        return f"{start_line}–{end_line}" if start_line != end_line else str(start_line)
        except Exception:
            pass
        return ""

    @staticmethod
    def validate_and_format_citations(
        claimed_indices: List[int],
        retrieved_hits: List[Dict[str, Any]],
        expected_machine_code: str,
        media_url_base: str = "/media/manuals/"
    ) -> List[Dict[str, Any]]:
        """
        Takes source indices used by LLM (1-based), validates them strictly
        against retrieved_hits and expected machine_code, and formats verified citations.
        """
        verified = []
        seen_keys = set()

        for idx_1based in claimed_indices:
            idx = idx_1based - 1
            if not (0 <= idx < len(retrieved_hits)):
                continue

            hit = retrieved_hits[idx]
            meta = hit.get("metadata", {})

            # Machine isolation safety check
            if meta.get("machine_id") != expected_machine_code:
                continue

            doc_id = meta.get("document_id", "")
            doc_name = meta.get("document_name", doc_id)
            revision = meta.get("revision", "1.0")
            page_no = int(meta.get("page_number", 1))
            filename = meta.get("filename", "") or f"{doc_name}.pdf"
            passage = hit.get("text", "")

            # Deduplicate by document + page
            dedup_key = (doc_id, page_no)
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            # Build direct browser PDF page URL: /media/manuals/HP200_Operations_Rev1_0.pdf#page=2
            pdf_url = f"{media_url_base.rstrip('/')}/{filename}#page={page_no}"
            line_range = CitationService.calculate_line_range(doc_id, page_no, passage)

            verified.append({
                "source_index": idx_1based,
                "document_name": doc_name,
                "document_id": doc_id,
                "revision": revision,
                "pdf_page": page_no,
                "line_range": line_range,
                "supporting_passage": passage,
                "pdf_url": pdf_url,
                "manual_id": meta.get("manual_id"),
                "similarity": hit.get("similarity", 0.0),
            })

        return verified

