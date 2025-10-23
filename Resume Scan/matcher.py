from sentence_transformers import SentenceTransformer, util
import re

#Model config
modelName = 'all-MiniLM-L6-v2'
minKeywordLen = 4  #Increased from 3 to reduce noise

#Expanded stopwords to filter generic terms
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

#Keyword categories for better organization
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

#Global model instance loaded lazily
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
            not token.isdigit())  #Remove pure numbers like "100", "9"
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
    """Calculate semantic similarity and keyword overlap. Returns (score, matched, missing)."""
    
    m = loadModel()
    jobEmb = m.encode(jobDesc, convert_to_tensor=True)
    resumeEmb = m.encode(resumeText, convert_to_tensor=True)
    score = util.pytorch_cos_sim(jobEmb, resumeEmb).item()
    
    jobKeywords = extractKeywords(jobDesc)
    resumeKeywords = extractKeywords(resumeText)
    
    matched = jobKeywords & resumeKeywords
    missing = jobKeywords - resumeKeywords
    
    return score, matched, missing