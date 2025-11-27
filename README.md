# AI Resume Scanner

A CLI tool developed to analyze PDF resumes against job descriptions using Google's Gemini models.

## Dependencies

* Python 3.x
* `pymupdf`
* `beautifulsoup4`
* `requests`
* `google-generativeai`

## Installation

1.  **Install libraries:**
    ```bash
    pip install pymupdf beautifulsoup4 requests google-generativeai
    ```

2.  **Configuration:**
    * Rename `secrets_config.example.py` to `secrets_config.py`.
    * Open the file and paste your Google API Key where indicated.

## Usage

1.  **Preparation:** Ensure your Resume PDF is located in the same folder as these scripts.
2.  **Run the script:**
    ```bash
    python main.py
    ```
3.  Follow the prompts to input the Job URL and your Resume filename.