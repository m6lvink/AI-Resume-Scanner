# Resume Matcher

Analyze how well your resume matches a job description using AI semantic similarity and keyword matching.

## Architecture

Frontend: HTML/CSS/JavaScript (vanilla)
Backend: Python Flask REST API
Model: sentence-transformers (MiniLM)

## Setup

```bash
pip install -r requirements.txt
```

First run downloads the AI model (80MB) - takes 10-20 seconds.

## Usage

```bash
python server.py
```

Open browser to `http://localhost:5000`

1. Paste job description in left panel
2. Drag and drop resume PDF in right panel (or click to browse)
3. Click "Analyze Match"
4. View results with categorized keywords
5. Download results as text file

## Features

- Drag and drop PDF upload
- Real-time semantic analysis (0-100% match score)
- Keyword extraction and matching
- Categorized skills (languages, frameworks, tools, databases)
- Tabbed results view
- Download results as text

## API Endpoints

### POST /api/analyze
Analyze resume against job description

Request (multipart/form-data):
- `jobDesc`: Job description text
- `resume`: PDF file

Response (JSON):
```json
{
  "score": 85.3,
  "matched": ["python", "react", "docker"],
  "missing": ["kubernetes", "terraform"],
  "matchedCategories": {
    "languages": ["python"],
    "frameworks": ["react"],
    "tools": ["docker"],
    "databases": [],
    "other": []
  },
  "missingCategories": {...}
}
```

## File Structure

```
/project
├── server.py              # Flask backend with API
├── resumeParser.py        # PDF text extraction
├── matcher.py             # AI scoring and keyword matching
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── style.css         # All styling
│   └── script.js         # Frontend logic
└── templates/
    └── index.html        # Main page
```

## Performance

- Analysis time: 2-4 seconds (after model loads)
- Model load: 10-20 seconds on first run (cached after)
- PDF parsing: <1 second
- Max file size: 50MB

## Limitations

- PDF only (no DOCX)
- Image-based/scanned PDFs need OCR (not included)
- Encrypted PDFs not supported
- English only

## Score Interpretation

- 75%+ = Strong match
- 60-75% = Good match
- 45-60% = Moderate match
- <45% = Weak match