from sentence_transformers import SentenceTransformer, util
import re

# Model configuration
MODEL_NAME = 'all-MiniLM-L6-v2'
MIN_KEYWORD_LENGTH = 4  # Increased from 3 to reduce noise

# Expanded stopwords to filter more generic terms: Seems to be working better after doubling size :O
STOPWORDS = {
    'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
    'has', 'have', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'may', 'might', 'must', 'can', 'this',
    'that', 'these', 'those', 'with', 'from', 'as', 'by', 'about',
    'also', 'between', 'work', 'general', 'current', 'expected',
    'designed', 'maintaining', 'than', 'more', 'most', 'other',
    'such', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'under', 'again', 'further', 'then', 'once', 'here',
    'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own',
    'same', 'than', 'too', 'very', 'just', 'being', 'doing', 'having'
}

# Global model instance loaded lazily to avoid startup delay
_model = None

def loadModel():
    """
    Lazy load the sentence transformer model on first use.
    Avoids 2-3 second startup delay if model is never used.
    Model is cached in global _model after first load.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def extractKeywords(text):
    """
    Extract meaningful keywords from text for matching.
    
    Process:
        1. Lowercase entire text for case-insensitive matching
        2. Extract alphanumeric tokens including special chars like C++, Node.js
        3. Filter out stopwords and tokens shorter than MIN_KEYWORD_LENGTH
        4. Remove numeric-only tokens
    
    Args:
        text: Raw text to extract keywords from
    
    Returns:
        set: Lowercase keywords with stopwords removed
    
    Examples:
        "Python, JavaScript and React" -> {'python', 'javascript', 'react'}
        "Senior Software Engineer" -> {'senior', 'software', 'engineer'}
    """
    textLower = text.lower()
    
    # Match alphanumeric with +, #, . for tech terms (C++, C#, Node.js)
    tokens = re.findall(r'\b[a-z0-9+#.]+\b', textLower)
    
    # Filter short tokens, stopwords, and pure numbers
    keywords = {
        token for token in tokens
        if (len(token) >= MIN_KEYWORD_LENGTH and 
            token not in STOPWORDS and
            not token.isdigit())  # Remove pure numbers like "100", "9"
    }
    return keywords

def getMatchScore(jobDesc, resumeText):
    """
    Calculate semantic similarity and keyword overlap between job and resume.
    
    Uses two complementary approaches:
        1. Semantic similarity via sentence embeddings (0-1 score)
        2. Exact keyword matching for specific skills/technologies
    
    Args:
        jobDesc: Job description text
        resumeText: Resume text content
    
    Returns:
        tuple: (similarityScore, matchedKeywords, missingKeywords)
            similarityScore: float in [0, 1] from cosine similarity
            matchedKeywords: set of keywords present in both texts
            missingKeywords: set of keywords in job but not in resume
    
    Raises:
        ValueError: if either input is empty or whitespace-only
        RuntimeError: if model encoding fails (OOM, CUDA errors)
    
    Performance:
        Typical runtime 200-400ms on CPU for 500-word texts with model cached.
        First run adds 2-3s for model download and initialization.
    """
    # Validate inputs are non-empty to avoid silent failures
    if not jobDesc or not jobDesc.strip():
        raise ValueError("jobDesc cannot be empty")
    if not resumeText or not resumeText.strip():
        raise ValueError("resumeText cannot be empty")
    
    # Encode texts to embeddings and calculate cosine similarity
    try: 
        m = loadModel()
        jobEmb = m.encode(jobDesc, convert_to_tensor=True)
        resumeEmb = m.encode(resumeText, convert_to_tensor=True)
        # Returns tensor with single similarity value
        score = util.pytorch_cos_sim(jobEmb, resumeEmb).item()
    except Exception as e:
        raise RuntimeError(f"model encoding failed: {e}")
    
    # Extract and compare keywords for explicit skill matching
    jobKeywords = extractKeywords(jobDesc)
    resumeKeywords = extractKeywords(resumeText)
    
    # Set intersection for skills present in both
    matched = jobKeywords & resumeKeywords
    # Set difference for skills in job but not resume (gaps to address)
    missing = jobKeywords - resumeKeywords
    
    return score, matched, missing