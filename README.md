# AI-Resume-Scanner: Python Resume Scanner 

A small Python project that provides tools to scan resumes and extract structured information using AI-assisted methods.

Why it exists
- Convert unstructured resumes into structured data to reduce manual screening time.
- Provide a foundation for building automated resume scoring, parsing, or extraction workflows.
- Quick check to see if your resume is "optimal" for a position

Quick start

1. Clone the repository:
```bash
git clone https://github.com/m6lvink/AI-Resume-Scanner.git
cd AI-Resume-Scanner
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Install dependencies:
   
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Edits
Below are general examples you can adapt in the code:

- Run as a module (replace `resume_scan` with the actual module name if present):
```bash
python -m resume_scan path/to/resume.pdf
```

- Import from Python and run a scanner class or function (replace names with actual ones found in the code):
```python
from resume_scan import Scanner

scanner = Scanner()
result = scanner.scan("resume.pdf")
print(result)
```

Links
- Issues: https://github.com/m6lvink/AI-Resume-Scanner/issues
- Repository: https://github.com/m6lvink/AI-Resume-Scanner
