"""
Citation validation and PDF navigation service.
Validates citations against actual retrieved source chunks, ensures no hallucinated
page numbers, and constructs working /media/manuals/<pdf>#page=<page> viewer URLs.
"""
from typing import List, Dict, Any, Optional

class CitationService:
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

            verified.append({
                "source_index": idx_1based,
                "document_name": doc_name,
                "document_id": doc_id,
                "revision": revision,
                "pdf_page": page_no,
                "supporting_passage": passage,
                "pdf_url": pdf_url,
                "manual_id": meta.get("manual_id"),
                "similarity": hit.get("similarity", 0.0),
            })

        return verified

