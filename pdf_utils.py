import fitz  # PyMuPDF
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFParsingError(Exception):
    """Custom exception for PDF parsing errors."""
    pass

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text content from a PDF file using PyMuPDF.
    Args:
        pdf_path: The file path to the PDF.
    Returns:
        The extracted text as a single string.
    Raises:
        PDFParsingError if the file doesn't exist or text extraction fails.
    """
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise PDFParsingError(f"PDF file not found: {pdf_path}")

    try:
        logger.info(f"Opening PDF for text extraction: {pdf_path}")
        doc = fitz.open(pdf_path)
        text_parts = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text:
                text_parts.append(page_text)
        doc.close()
        
        full_text = "\n\n--- End of Page ---\n\n".join(text_parts)
        
        if not full_text.strip():
            logger.warning(f"No text could be extracted from PDF: {pdf_path}. It might be image-based or empty.")
            raise PDFParsingError(f"No text could be extracted from PDF: {pdf_path}. The PDF might be image-based, contain no selectable text, or be corrupted.")
        
        logger.info(f"Successfully extracted text from {pdf_path}. Length: {len(full_text)} characters.")
        return full_text
    except Exception as e:
        logger.error(f"Failed to parse PDF {pdf_path}: {e}", exc_info=True)
        raise PDFParsingError(f"An error occurred while parsing the PDF '{os.path.basename(pdf_path)}': {str(e)}")