//Global state
let uploadedFile = null;
let resultsData = null;
let currentMatchedTab = 'all';
let currentMissingTab = 'all';

//Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupFileUpload();
    setupCharCounter();
});

//Character counter for job description
function setupCharCounter() {
    const jobDesc = document.getElementById('jobDesc');
    const charCount = document.getElementById('charCount');
    
    jobDesc.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
}

//File upload setup
function setupFileUpload() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    
    //Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    //Highlight dropzone on drag
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.add('dragover');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.remove('dragover');
        });
    });
    
    //Handle drop
    dropzone.addEventListener('drop', handleDrop);
    
    //Handle file select
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    //Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('File must be a PDF');
        return;
    }
    
    //Validate file size
    const maxSize = 50 * 1024 * 1024; //50MB
    if (file.size > maxSize) {
        showError('File size exceeds 50MB limit');
        return;
    }
    
    uploadedFile = file;
    
    //Update UI
    document.querySelector('.dropzone-content').style.display = 'none';
    document.getElementById('fileInfo').style.display = 'block';
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
}

function clearFile() {
    uploadedFile = null;
    document.getElementById('fileInput').value = '';
    document.querySelector('.dropzone-content').style.display = 'block';
    document.getElementById('fileInfo').style.display = 'none';
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

//Analysis
async function analyze() {
    const jobDesc = document.getElementById('jobDesc').value;
    
    //Validate inputs
    if (!jobDesc.trim()) {
        showError('Please enter a job description');
        return;
    }
    
    if (!uploadedFile) {
        showError('Please upload a resume PDF');
        return;
    }
    
    //Prepare form data
    const formData = new FormData();
    formData.append('jobDesc', jobDesc);
    formData.append('resume', uploadedFile);
    
    //Show loading
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('results').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        //Check if response is ok before parsing JSON
        if (!response.ok) {
            let errorMsg = 'Analysis failed';
            try {
                const data = await response.json();
                errorMsg = data.error || errorMsg;
            } catch (e) {
                //Response is not JSON, might be HTML error page
                const text = await response.text();
                console.error('Server error response:', text);
                errorMsg = 'Server error - check console for details';
            }
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        
        //Store results
        resultsData = data;
        
        //Display results
        displayResults(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById('analyzeBtn').disabled = false;
        document.getElementById('loading').style.display = 'none';
    }
}

function displayResults(data) {
    //Update metrics
    document.getElementById('scoreValue').textContent = data.score + '%';
    document.getElementById('matchedCount').textContent = data.matched.length;
    document.getElementById('missingCount').textContent = data.missing.length;
    
    //Update score bar
    const scoreBar = document.getElementById('scoreBar');
    scoreBar.style.width = data.score + '%';
    
    //Update score message
    const scoreMessage = document.getElementById('scoreMessage');
    if (data.score >= 65) {
        scoreMessage.textContent = 'Strong match';
        scoreMessage.className = 'score-message strong';
    } else if (data.score >= 50) {
        scoreMessage.textContent = 'Good match';
        scoreMessage.className = 'score-message good';
    } else if (data.score >= 35) {
        scoreMessage.textContent = 'Moderate match';
        scoreMessage.className = 'score-message moderate';
    } else {
        scoreMessage.textContent = 'Weak match';
        scoreMessage.className = 'score-message weak';
    }
    
    //Display matched keywords
    currentMatchedTab = 'all';
    displayKeywords('matched', data.matched, 'all');
    
    //Display missing keywords
    currentMissingTab = 'all';
    displayKeywords('missing', data.missing, 'all');
    
    //Show results section
    document.getElementById('results').style.display = 'block';
    
    //Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function displayKeywords(type, keywords, category) {
    const contentId = type === 'matched' ? 'matchedContent' : 'missingContent';
    const content = document.getElementById(contentId);
    const cssClass = type === 'matched' ? 'matched' : 'missing';
    
    //Get keywords for category
    let keywordsToShow = [];
    if (category === 'all') {
        keywordsToShow = keywords;
    } else {
        const categoriesKey = type === 'matched' ? 'matchedCategories' : 'missingCategories';
        keywordsToShow = resultsData[categoriesKey][category] || [];
    }
    
    //Display keywords
    if (keywordsToShow.length === 0) {
        content.innerHTML = '<p style="color: #666;">None</p>';
    } else {
        content.innerHTML = keywordsToShow
            .map(kw => `<span class="keyword-tag ${cssClass}">${kw}</span>`)
            .join('');
    }
}

function switchTab(type, category) {
    //Update tab buttons
    const parentSection = document.querySelector(`#${type}Content`).closest('.keywords-section');
    const tabs = parentSection.querySelectorAll('.tab-btn');
    tabs.forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    //Update current tab tracking
    if (type === 'matched') {
        currentMatchedTab = category;
        displayKeywords('matched', resultsData.matched, category);
    } else {
        currentMissingTab = category;
        displayKeywords('missing', resultsData.missing, category);
    }
}

function downloadResults() {
    if (!resultsData) return;
    
    const text = `RESUME MATCH REPORT
${'='.repeat(50)}
Match Score: ${resultsData.score}%
Matched Skills: ${resultsData.matched.length}
Missing Keywords: ${resultsData.missing.length}

MATCHED SKILLS (${resultsData.matched.length}):
${resultsData.matched.join(', ')}

MISSING KEYWORDS (${resultsData.missing.length}):
${resultsData.missing.join(', ')}
`;
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resume_match_report.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function showError(message) {
    const error = document.getElementById('error');
    error.textContent = message;
    error.style.display = 'block';
    
    //Scroll to error
    error.scrollIntoView({ behavior: 'smooth' });
    
    //Hide after 5 seconds
    setTimeout(() => {
        error.style.display = 'none';
    }, 5000);
}