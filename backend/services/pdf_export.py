import io
import logging

WEASYPRINT_INSTALLED = False
_WEASYPRINT_ERROR = None

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_INSTALLED = True
except Exception as exc:
    WEASYPRINT_INSTALLED = False
    _WEASYPRINT_ERROR = str(exc)

logger = logging.getLogger('ats_resume_scorer')

def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
    if not WEASYPRINT_INSTALLED:
        err_msg = _WEASYPRINT_ERROR or "WeasyPrint is not installed or GTK3 system libraries are missing."
        logger.error(f"PDF generation failed due to missing dependencies: {err_msg}")
        raise RuntimeError(f"PDF generation unavailable on this host: {err_msg}")

    documents = []

    # Render HTML strings to WeasyPrint Document objects
    for name, html_str in html_docs.items():
        doc = HTML(string=html_str).render()
        documents.append(doc)

    if not documents:
        raise ValueError("No HTML documents provided for PDF generation.")

    # Merge them into the first document
    first_doc = documents[0]
    for other_doc in documents[1:]:
        for page in other_doc.pages:
            first_doc.pages.append(page)

    # Write combined PDF bytes
    pdf_bytes = first_doc.write_pdf()
    return pdf_bytes