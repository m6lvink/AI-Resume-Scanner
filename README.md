# Resume Matcher

Analyze how well a resume matches a job description using content similarity and keyword matching.

## Architecture

- Frontend: HTML, CSS, JavaScript (vanilla)
- Backend: Flask (Python) REST API
- Text processing: content similarity + keyword extraction

## Prerequisites

- Python 3.9+
- pip

## Setup

Create a virtual environment (recommended) and install dependencies:

**Windows (PowerShell):**
```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Note:** The first analysis downloads an AI model (~80MB) and caches it for future use.

## Usage

Start the development server:

**Windows (PowerShell):**
```powershell
python server.py
```

**macOS/Linux:**
```bash
python3 server.py
```

Then open: http://localhost:5000

**Steps:**
1. Paste the job description in the left panel
2. Drag and drop a resume PDF in the right panel (or click to browse)
3. Click "Analyze Match"
4. Review results with categorized keywords
5. Download results as a text file if needed

## Features

- Drag and drop PDF upload
- Smart weighted scoring (semantic 60% + keyword match 40%)
- Focuses on technical keywords (languages, frameworks, tools, databases)
- Keyword extraction and categorization
- Tabbed results view
- Download results as text
- Max file size: 50MB

## API

### POST /api/analyze

Analyze a resume against a job description.

**Request (multipart/form-data):**
- `jobDesc`: Job description text
- `resume`: PDF file

**Response (JSON):**
```json
{
  "score": 72.5,
  "matched": ["python", "react", "docker"],
  "missing": ["kubernetes", "terraform"],
  "matchedCategories": {
    "languages": ["python"],
    "frameworks": ["react"],
    "tools": ["docker"],
    "databases": [],
    "other": []
  },
  "missingCategories": {
    "languages": [],
    "frameworks": [],
    "tools": ["kubernetes", "terraform"],
    "databases": [],
    "other": []
  }
}
```

## File Structure

```
.
├── server.py              # Flask backend and API
├── resumeParser.py        # PDF text extraction
├── matcher.py             # Scoring and keyword matching
├── requirements.txt       # Python dependencies
├── test_matcher.py        # Basic matcher tests
├── static/
│   ├── style.css          # Styles
│   └── script.js          # Frontend logic
└── templates/
    └── index.html         # Main page
```

## Performance

- Analysis time: 2-4 seconds (after model loads)
- Model load: 10-20 seconds on first run (cached after)
- PDF parsing: <1 second for typical resumes
- Max file size: 50MB

## Limitations

- PDF only (no DOCX)
- Image/scanned PDFs require OCR (not included)
- Encrypted PDFs not supported
- English only

## Score Guide

- **65%+ = Strong match**
- **50-65% = Good match**
- **35-50% = Moderate match**
- **<35% = Weak match**

## Scoring Methodology

Final score combines:
- **Semantic similarity (60%)**: Overall content alignment using AI
- **Keyword match (40%)**: Technical skills match (languages, frameworks, tools, databases only)

Generic keywords in the "other" category are shown but don't affect your score.

**Example:**
- Job posting has 250 total keywords
  - 20 technical (python, react, docker, etc.)
  - 230 generic (experience, working, team, etc.)
- Your resume matches 15/20 technical skills
- Old approach: 15/250 = 6% (harsh)
- New approach: Semantic 70% + Keywords 75% (15/20) = 72% (realistic)

## Troubleshooting

**Template not found:**
- Ensure you run `server.py` from the directory containing `templates/` and `static/` folders
- Check folder structure matches the layout above

**Paths with spaces (Windows):**
- Always quote paths: `python "path with spaces/server.py"`

**Slow first run:**
- Model downloads on first analysis (~80MB)
- Wait 10-20 seconds, happens only once

**JSON error:**
- Check browser console (F12) for details
- Verify all dependencies installed: `pip install -r requirements.txt`
- Run test script: `python test_matcher.py`

**Import errors:**
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## Development

**Test matcher:**
```bash
python test_matcher.py
```

**Dependencies:**
- flask==3.0.0
- sentence-transformers==3.3.1
- pymupdf==1.24.14

## Notes

- This is a development server - not for production use
- For production, use a WSGI server (gunicorn, uwsgi)
- Server runs on http://127.0.0.1:5000 by default
- Press Ctrl+C to stop the server
