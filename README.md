# AI Resume Scanner

CLI tool that analyzes PDF resumes against job descriptions using Google Gemini models.

## Requirements

Python 3.x

Required packages:
- pymupdf
- beautifulsoup4
- requests
- google-generativeai

## Installation

Install dependencies:
```bash
pip install pymupdf beautifulsoup4 requests google-generativeai
```

Configure API key:
1. Rename `secrets_config.example.py` to `secrets_config.py`
2. Add your Google API key to the file

## Usage

Run the script:
```bash
python main.py
```

Enter the job posting URL and resume PDF path when prompted.