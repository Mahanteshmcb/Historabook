import fitz  # PyMuPDF
import logging

def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """
    Opens a PDF from bytes and extracts text page by page.
    Returns: {"full_text": str, "page_count": int}
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = []
    
    for page in doc:
        # FIX: Pylance gets confused by fitz types, so we ignore strict checking here
        text = page.get_text() # type: ignore
        full_text.append(text)
        
    return {
        "full_text": "\n".join(full_text),
        "page_count": len(doc)
    }