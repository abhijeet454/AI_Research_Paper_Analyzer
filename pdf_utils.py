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
        logger.error(f"PDF file not found at specified path: {pdf_path}")
        raise PDFParsingError(f"PDF file not found: {pdf_path}")

    try:
        logger.info(f"Opening PDF for text extraction: {os.path.basename(pdf_path)}")
        doc = fitz.open(pdf_path)
        text_parts = [page.get_text("text") for page in doc]
        doc.close()

        full_text = "\n\n".join(filter(None, text_parts))

        if not full_text.strip():
            logger.warning(f"No text could be extracted from {os.path.basename(pdf_path)}. It might be image-based or empty.")
            raise PDFParsingError(f"No text could be extracted from '{os.path.basename(pdf_path)}'. The PDF might be image-based or contain no selectable text.")

        logger.info(f"Successfully extracted {len(full_text)} characters from {os.path.basename(pdf_path)}.")
        return full_text
    except Exception as e:
        logger.error(f"Failed to parse PDF {os.path.basename(pdf_path)}: {e}", exc_info=True)
        raise PDFParsingError(f"An error occurred while parsing '{os.path.basename(pdf_path)}': {str(e)}")