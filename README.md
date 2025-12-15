# AI Resume Scanner

CLI tool that analyzes PDF resumes against job descriptions using Google Gemini models.

## Requirements

Python 3.x

Required packages:
- pymupdf
- beautifulsoup4
- requests
- google-generativeai
- python-dotenv

## Installation

Install dependencies:
```bash
pip install pymupdf beautifulsoup4 requests google-generativeai python-dotenv
```

Configure API key:
1. Copy `.env.example` to `.env`
2. Add your Google API key to the `.env` file

## Usage

Run the script:
```bash
python main.py
```

Enter the job posting URL and resume PDF path when prompted.