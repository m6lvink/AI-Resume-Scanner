import fitz  # PyMuPDF library

def extractTextFromPdf(filePath):
    """
    Extract text content from PDF file with error handling.
    
    Process:
        1. Open PDF and verify it's not encrypted
        2. Iterate through all pages extracting text
        3. Join page texts and normalize whitespace
        4. Close document in all cases (success or error)
    
    Args:
        filePath: Path to PDF file on filesystem
    
    Returns:
        str: Extracted text with normalized whitespace (multiple spaces/newlines
             collapsed to single space)
    
    Raises:
        FileNotFoundError: if filePath does not exist
        ValueError: if file is not a valid PDF format
        RuntimeError: if PDF is encrypted, corrupted, or page extraction fails
    
    Limitations:
        - Image-only PDFs (scanned documents) return empty string
        - No OCR support for scanned documents
        - Encrypted PDFs cannot be processed even if user has password
        - Complex layouts may have incorrect text ordering
    
    Performance:
        Typical speed 10-50 pages/second depending on PDF complexity.
        Memory usage scales with file size (approx 2-3x file size).
    """
    # Open PDF with validation of file format
    try:
        doc = fitz.open(filePath)
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF not found: {filePath}")
    except Exception as e:
        raise ValueError(f"invalid PDF format: {e}")
    
    # Check for password protection before attempting extraction
    if doc.is_encrypted:
        doc.close()
        raise RuntimeError(f"PDF is password-protected: {filePath}")
    
    try:
        textParts = []
        # Extract text from each page with per-page error handling
        for pageNum, page in enumerate(doc, start=1):
            try:
                pageText = page.get_text()
                if pageText:  # Skip empty pages
                    textParts.append(pageText)
            except Exception as e:
                doc.close()
                raise RuntimeError(
                    f"failed to extract text from page {pageNum}: {e}"
                )
        
        doc.close()
        
        # Combine all page texts with newlines
        fullText = "\n".join(textParts)
        
        # Normalize whitespace: collapse multiple spaces/newlines to single space
        # This makes keyword matching more reliable and reduces noise
        normalized = " ".join(fullText.split())
        return normalized
        
    except Exception as e:
        # Ensure document is always closed even if unexpected error occurs
        doc.close() 
        raise RuntimeError(f"PDF processing error: {e}")