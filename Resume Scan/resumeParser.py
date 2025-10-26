import fitz

def extractTextFromPdf(filePath):
    """Extract text from PDF. Returns normalized text."""
    
    doc = fitz.open(filePath)
    
    if doc.is_encrypted:
        doc.close()
        raise RuntimeError(f"PDF is password-protected: {filePath}")
    
    textParts = []
    for page in doc:
        pageText = page.get_text()
        if pageText:
            textParts.append(pageText)
    
    doc.close()
    
    fullText = "\n".join(textParts)
    normalized = " ".join(fullText.split())
    return normalized