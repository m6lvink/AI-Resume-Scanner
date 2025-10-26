from flask import Flask, render_template, request, jsonify
import os
import tempfile
from resumeParser import extractTextFromPdf
from matcher import getMatchScore, categorizeKeywords

# Ensure Flask can find templates/static that live one level up
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_BASE_DIR, '..'))
app = Flask(
    __name__,
    template_folder=os.path.join(_PROJECT_ROOT, 'templates'),
    static_folder=os.path.join(_PROJECT_ROOT, 'static')
)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  #50MB max

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        #Validate inputs
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file'}), 400
        if 'jobDesc' not in request.form:
            return jsonify({'error': 'No job description'}), 400
        
        resumeFile = request.files['resume']
        jobDesc = request.form['jobDesc']
        
        if resumeFile.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not resumeFile.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be PDF'}), 400
        
        if not jobDesc.strip():
            return jsonify({'error': 'Job description is empty'}), 400
        
        #Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
            resumeFile.save(temp.name)
            tempPath = temp.name
        
        try:
            #Extract text from PDF
            resumeText = extractTextFromPdf(tempPath)
            
            if not resumeText.strip():
                return jsonify({'error': 'No text in PDF'}), 400
            
            #Calculate match score
            score, matched, missing = getMatchScore(jobDesc, resumeText)
            
            #Categorize keywords
            matchedCats = categorizeKeywords(matched)
            missingCats = categorizeKeywords(missing)
            
            #Build response
            result = {
                'score': round(score * 100, 1),
                'matched': sorted(list(matched)),
                'missing': sorted(list(missing)),
                'matchedCategories': {
                    'languages': sorted(list(matchedCats['languages'])),
                    'frameworks': sorted(list(matchedCats['frameworks'])),
                    'tools': sorted(list(matchedCats['tools'])),
                    'databases': sorted(list(matchedCats['databases'])),
                    'other': sorted(list(matchedCats['other']))
                },
                'missingCategories': {
                    'languages': sorted(list(missingCats['languages'])),
                    'frameworks': sorted(list(missingCats['frameworks'])),
                    'tools': sorted(list(missingCats['tools'])),
                    'databases': sorted(list(missingCats['databases'])),
                    'other': sorted(list(missingCats['other']))
                }
            }
            
            return jsonify(result)
            
        finally:
            #Cleanup temp file
            if os.path.exists(tempPath):
                os.remove(tempPath)
    
    except Exception as e:
        #Ensure we always return valid JSON
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
