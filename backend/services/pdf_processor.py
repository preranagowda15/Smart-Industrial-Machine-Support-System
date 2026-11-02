"""
PDF extraction service using PyMuPDF (fitz).
Extracts text page-by-page while preserving 1-based physical PDF page numbers.
"""
from pathlib import Path
from typing import List, Dict, Any, Union
import pymupdf  # PyMuPDF

class PDFProcessor:
    @staticmethod
    def extract_pages(pdf_source: Union[str, Path, bytes]) -> List[Dict[str, Any]]:
        """
        Extracts text from each page of a PDF document.
        Returns a list of dicts:
        [
            {
                "page_number": 1,  # 1-based index
                "text": "Extracted page text...",
                "char_count": 123
            },
            ...
        ]
        """
        if isinstance(pdf_source, (str, Path)):
            doc = pymupdf.open(str(pdf_source))
        elif isinstance(pdf_source, bytes):
            doc = pymupdf.open(stream=pdf_source, filetype="pdf")
        else:
            doc = pymupdf.open(pdf_source)

        pages = []
        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                # Page numbers are strictly 1-based for human reference and browser viewer #page=X
                page_number = page_index + 1
                raw_text = page.get_text("text") or ""
                # Normalize whitespace but keep basic sentence structure
                cleaned_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
                cleaned_text = "\n".join(cleaned_lines)
                
                pages.append({
                    "page_number": page_number,
                    "text": cleaned_text,
                    "char_count": len(cleaned_text),
                })
        finally:
            doc.close()

        return pages

    @staticmethod
    def get_page_count(pdf_source: Union[str, Path, bytes]) -> int:
        """Returns the total number of pages in the PDF."""
        if isinstance(pdf_source, (str, Path)):
            doc = pymupdf.open(str(pdf_source))
        elif isinstance(pdf_source, bytes):
            doc = pymupdf.open(stream=pdf_source, filetype="pdf")
        else:
            doc = pymupdf.open(pdf_source)
        try:
            return len(doc)
        finally:
            doc.close()
