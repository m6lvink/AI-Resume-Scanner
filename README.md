# Resume Matcher

AI-powered resume analyzer that compares your resume against job descriptions using semantic similarity and keyword matching.

## Setup

```bash
pip install -r requirements.txt
```

First run downloads the AI model (80MB) - takes 10-20 seconds.

## Usage

### Web UI
```bash
streamlit run app.py
```
Opens browser at `http://localhost:8501`

Features:
- Drag and drop PDF upload
- Real-time match scoring
- Categorized skills (languages, frameworks, tools, databases)
- Visual progress bars and metrics
- Download results as text file

### Command Line
```bash
python main.py
```
- Paste job description (press ENTER twice to finish)
- Enter path to PDF resume
- View match score and keyword analysis

## How It Works

1. PDF Parsing: Extracts text from resume PDF
2. Semantic Analysis: Uses sentence transformers (MiniLM model) to calculate similarity score (0-100%)
3. Keyword Matching: Extracts technical terms and compares job requirements vs resume
4. Gap Analysis: Shows which skills you have and which are missing

## Files

- `app.py` - Streamlit web interface with drag-and-drop
- `main.py` - Command line interface
- `resumeParser.py` - PDF text extraction
- `matcher.py` - AI scoring and keyword analysis
- `requirements.txt` - Python dependencies

## Performance

- Web UI: 2-4 seconds per analysis (after model loads)
- Model load: 10-20 seconds on first run (cached after)
- PDF parsing: <1 second for typical resumes
- Max file size: 50MB

## Limitations

- PDF only (no DOCX support yet)
- Image-based/scanned PDFs need OCR (not included)
- Encrypted PDFs not supported
- English language only

## Tips

- Use specific technical terms from job posting in resume
- Add missing keywords naturally to your experience sections
- 75%+ match = strong alignment
- 60-75% = good match
- <60% = consider tailoring resume more