import sys
import os
from resumeParser import extractTextFromPdf
from matcher import getMatchScore

def readMultilineInput(prompt):
    """Read multi-line input until empty line. Returns stripped text with newlines."""
    print(prompt)
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()

def validateFilePath(path):
    """Validate file exists and is valid PDF. Returns None if valid, error message if invalid."""
    if not path:
        return "FILE_PATH_EMPTY: provide a file path"
    if not os.path.exists(path):
        return f"FILE_NOT_FOUND: {path} does not exist"
    if not path.lower().endswith('.pdf'):
        return f"INVALID_FORMAT: {path} must be a PDF file"
    
    fileSize = os.path.getsize(path)
    if fileSize == 0:
        return f"EMPTY_FILE: {path} has 0 bytes"
    if fileSize > 50 * 1024 * 1024:
        return f"FILE_TOO_LARGE: {path} exceeds 50MB"
    
    return None 

def main():
    #Read job description with multi-line support
    jobDesc = readMultilineInput(
        "Paste the job description. Press ENTER twice to finish:"
    )
    
    if not jobDesc:
        print("JOB_DESC_EMPTY: provide at least one line of text")
        sys.exit(1)
    
    #Get resume path and validate
    resumePath = input(
        "Enter path to your resume PDF (e.g., resume.pdf): "
    ).strip()
    
    error = validateFilePath(resumePath)
    if error:
        print(error)
        sys.exit(1)
    
    #Extract text from PDF
    try:
        resumeText = extractTextFromPdf(resumePath)
    except Exception as e:
        print(f"PDF_PARSE_ERROR: failed to extract text from {resumePath}: {e}")
        sys.exit(1)
    
    #Check if text was extracted (image-only PDFs return empty)
    if not resumeText.strip():
        print(f"NO_TEXT_EXTRACTED: {resumePath} contains no readable text. Try OCR or check if PDF is image-based.")
        sys.exit(1)
    
    #Calculate semantic similarity and keyword matching
    try:
        score, matched, missing = getMatchScore(jobDesc, resumeText)
    except Exception as e:
        print(f"MATCH_ERROR: scoring failed: {e}")
        sys.exit(1)
    
    #Display results with truncation for large keyword sets
    print(f"\nAI Match Score: {score * 100:.1f}%")
    
    print(f"\nMatched Skills ({len(matched)}):")
    if matched:
        displayMatched = sorted(matched)[:20]  #Show first 20 alphabetically
        print(", ".join(displayMatched))
        if len(matched) > 20:
            print(f"... and {len(matched) - 20} more")
    else:
        print("None")
    
    print(f"\nMissing Keywords ({len(missing)}):")
    if missing:
        displayMissing = sorted(missing)[:20]  #Show first 20 alphabetically
        print(", ".join(displayMissing))
        if len(missing) > 20:
            print(f"... and {len(missing) - 20} more")
    else:
        print("None")

if __name__ == "__main__":
    main()