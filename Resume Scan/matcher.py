from sentence_transformers import SentenceTransformer, util
import re

#Model config
modelName = 'all-MiniLM-L6-v2'
minKeywordLen = 4

#Stopwords to filter generic terms
stopwords = {
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

#Keyword categories
categories = {
    'languages': {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
        'php', 'swift', 'kotlin', 'go', 'rust', 'scala', 'perl', 'r',
        'matlab', 'shell', 'bash', 'powershell', 'sql', 'html', 'css'
    },
    'frameworks': {
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js',
        'express', 'fastapi', 'rails', 'laravel', '.net', 'asp.net',
        'next.js', 'nuxt', 'gatsby', 'redux', 'tensorflow', 'pytorch',
        'keras', 'scikit-learn', 'pandas', 'numpy', 'jquery', 'bootstrap',
        'tailwind', 'material-ui'
    },
    'tools': {
        'docker', 'kubernetes', 'git', 'jenkins', 'gitlab', 'github',
        'jira', 'confluence', 'slack', 'aws', 'azure', 'gcp',
        'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'webpack',
        'babel', 'vite', 'nginx', 'apache', 'linux', 'unix', 'windows',
        'macos', 'visual', 'vscode', 'intellij', 'eclipse', 'postman',
        'grafana', 'prometheus', 'datadog', 'splunk', 'elasticsearch',
        'kibana', 'logstash'
    },
    'databases': {
        'postgresql', 'mysql', 'mongodb', 'redis', 'cassandra',
        'dynamodb', 'oracle', 'sqlite', 'mariadb', 'sqlserver',
        'neo4j', 'couchdb', 'firebase', 'firestore', 'memcached',
        'influxdb', 'timescaledb', 'snowflake', 'bigquery', 'redshift'
    }
}

#Global model instance
_model = None

def loadModel():
    """Lazy load the model on first use. Cached after first load."""
    global _model
    if _model is None:
        _model = SentenceTransformer(modelName)
    return _model

def extractKeywords(text):
    """Extract meaningful keywords from text for matching."""
    textLower = text.lower()
    
    #Match alphanumeric with +, #, . for tech terms (C++, C#, Node.js)
    tokens = re.findall(r'\b[a-z0-9+#.]+\b', textLower)
    
    #Filter short tokens, stopwords, and pure numbers
    keywords = {
        token for token in tokens
        if (len(token) >= minKeywordLen and 
            token not in stopwords and
            not token.isdigit())
    }
    return keywords

def categorizeKeywords(keywords):
    """Group keywords by type: languages, frameworks, tools, databases, other."""
    result = {
        'languages': set(),
        'frameworks': set(),
        'tools': set(),
        'databases': set(),
        'other': set()
    }
    
    for kw in keywords:
        categorized = False
        for catName, catSet in categories.items():
            if kw in catSet:
                result[catName].add(kw)
                categorized = True
                break
        
        if not categorized:
            result['other'].add(kw)
    
    return result

def getMatchScore(jobDesc, resumeText):
    """
    Calculate weighted score combining semantic similarity and keyword matching.
    Returns (finalScore, matched, missing).
    
    Scoring strategy:
    - Semantic similarity: 60% weight (overall content alignment)
    - Keyword match: 40% weight (specific skills match)
    - Only categorized keywords (languages, frameworks, tools, databases) count toward score
    - Generic 'other' keywords shown but don't affect score
    """
    
    m = loadModel()
    jobEmb = m.encode(jobDesc, convert_to_tensor=True)
    resumeEmb = m.encode(resumeText, convert_to_tensor=True)
    semanticScore = util.pytorch_cos_sim(jobEmb, resumeEmb).item()
    
    jobKeywords = extractKeywords(jobDesc)
    resumeKeywords = extractKeywords(resumeText)
    
    matched = jobKeywords & resumeKeywords
    missing = jobKeywords - resumeKeywords
    
    #Categorize to focus on important technical keywords
    matchedCats = categorizeKeywords(matched)
    missingCats = categorizeKeywords(missing)
    
    #Count only technical keywords (not generic 'other' category)
    importantMatched = (len(matchedCats['languages']) + len(matchedCats['frameworks']) + 
                       len(matchedCats['tools']) + len(matchedCats['databases']))
    importantMissing = (len(missingCats['languages']) + len(missingCats['frameworks']) + 
                       len(missingCats['tools']) + len(missingCats['databases']))
    
    #Calculate keyword match score (0-1)
    totalImportant = importantMatched + importantMissing
    if totalImportant > 0:
        keywordScore = importantMatched / totalImportant
    else:
        #No technical keywords found, rely entirely on semantic score
        keywordScore = semanticScore
    
    #Weighted combination: 60% semantic, 40% keyword matching
    finalScore = (semanticScore * 0.6) + (keywordScore * 0.4)
    
    return finalScore, matched, missing