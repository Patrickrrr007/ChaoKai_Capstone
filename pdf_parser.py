"""PDF parsing utilities using pdfplumber."""
import pdfplumber
from typing import List, Optional
import os


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")
    
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < text_length:
            # Look for sentence endings near the end
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.7:  # If we found a good break point
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - chunk_overlap
    
    return [chunk for chunk in chunks if chunk]  # Remove empty chunks


def extract_metadata_from_pdf(pdf_path: str) -> dict:
    """
    Extract metadata from PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with metadata
    """
    metadata = {
        "filename": os.path.basename(pdf_path),
        "filepath": pdf_path,
        "pages": 0
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            metadata["pages"] = len(pdf.pages)
    except Exception as e:
        print(f"Warning: Could not extract metadata: {str(e)}")
    
    return metadata

