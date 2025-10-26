from sentence_transformers import SentenceTransformer, util
import re

#Model config
modelName = 'all-MiniLM-L6-v2'
minKeywordLen = 4

#Stopwords to filter generic terms
stopwords = {
    # Core
    'the','and','or','but','in','on','at','to','for','of','a','an','is','are','was','were','be','been',
    'has','have','had','do','does','did','will','would','should','could','may','might','must','can',
    'this','that','these','those','with','from','as','by','about','also','between','than','more','most',
    'other','such','into','through','during','before','after','above','below','under','again','further',
    'then','once','here','there','when','where','why','how','all','both','each','few','some','only','own',
    'same','too','very','just','being','doing','having','out','up','down','over','off','while','because',
    'if','so','nor','although','though','unless','until','since','ever','never','always','often','usually',
    'sometimes','any','every','either','neither','within','without','across','around','near','per','via',
    'who','whom','whose','which','what','whatever','whichever','it','its','itself','they','them','their',
    'theirs','themselves','you','your','yours','yourself','yourselves','we','our','ours','ourselves','etc',
    'already','another','else','everyone','still','someone','something','step','type','version','versions',
    'want','works','writes','matched','matches','matched','applicable','applicant','applicants','applicable',

    # Boilerplate
    'objective','summary','profile','overview','experience','work','employment','history','responsibilities',
    'responsibility','responsible','duties','tasks','tasked','role','roles','position','positions','project',
    'projects','education','school','university','college','background','references','contact','address',
    'phone','email','linkedin','portfolio','skills','skill','competencies','competency','abilities','ability',
    'strengths','weaknesses','certification','certifications','license','licenses','seeking','looking',
    'available','willing','relocate','relocation','remote','hybrid','onsite','authorized','authorization',
    'eligible','eligibility','general','current','expected','designed','maintaining','managed','managing',
    'lead','led','leading','support','supported','supporting','assisted','assisting','assist','help','helped',
    'collaborate','collaborated','collaborating','coordinate','coordinated','coordinating','participate',
    'participated','participating','involved','deliver','delivered','delivering','own','owned','owning',
    'posting','contracts','contract','candidate','candidates','clearance','recommendations','recommended',
    'recommend','recommending','participates','provides','processes','crucial','control','fit','fits',
    'posting','perform','performs','performs','someone','something','restless',

    # HR / Business / Resume Fluff
    'accessible','accommodation','accommodations','action','activities','advanced','aggressive','agile',
    'aiming','analytical','approach','aspirations','attend','automation','back','beautiful','behind',
    'brands','bring','business','career','cases','category','centric','challenge','characteristic',
    'clients','close','collected','color','comes','committed','company','connected','connection',
    'consideration','convention','cost','creativity','creators','cultivating','daily','derive','desire',
    'determination','directly','disabilities','disciplines','done','drinks','drive','driving','early','easy',
    'employees','empowered','empowers','encouraged','encourages','equal','essential','events','exciting',
    'exclusive','existing','explore','family','favorite','feedback','find','finding','focused','focuses',
    'free','fresh','functionality','functioning','functions','gather','globally','going','government','grasp',
    'group','grow','harness','hear','helps','hyper','identity','inclusion','incorporate','individuals',
    'initiative','innovation','inside','insiders','insights','insurance','intelligence','interview','iterate',
    'iterating','laws','leave','level','life','light','locations','love','lunches','meaning','meetings',
    'mental','mind','mondays','month','months','move','national','needed','needs','nice','nimble','offices',
    'ones','optimize','organizational','orientation','otherwise','outside','owns','paid','partnering',
    'passing','peers','perks','person','personalized','persons','place','please','plus','polygraph','power',
    'prioritize','privileges','problems','purposeful','promise','propose','protected','qualified','quarter',
    'race','ready','real','reasonable','reasons','receive','recruiter','regard','reimbursement','relational',
    'religion','requires','researchers','restricted','retail','rewarding','right','rights','risks','scope',
    'scoping','scrum','small','simple','smaller','sorted','sorting','status','stock','stories','sure','step',
    'strongly','supportive','sustain','sustained','synergy','systemic','tactical','takes','talent','teammates',
    'technical','tech','thorough','together','traffic','trusted','typically','understand','understanding',
    'united','user','value','values','varies','vision','views','visit','veteran','week','weeks','year','years',

    # Filler verbs / generic actions
    'boot','bugs','control','crucial','debating','depend','depends','dust','enhancing','estimates','gathering',
    'good','ides','interact','interface','matched','melts','migrates','mold','posting','provides','ranging',
    'recommendations','recommended','scheming','scope','settles','small','someone','something','still','step',
    'substituted','tracking','type','upgrades','version','versions','want','works','writes',

    # Time/date words
    'january','february','march','april','may','june','july','august','september','october','november',
    'december','jan','feb','mar','apr','jun','jul','aug','sep','sept','oct','nov','dec','monday','tuesday',
    'wednesday','thursday','friday','saturday','sunday','mon','tue','tues','wed','thu','thur','thurs','fri',
    'sat','sun','spring','summer','autumn','fall','winter','today','yesterday','tomorrow','weekly','monthly',
    'quarterly','annually','yearly','present','previous','prior',

    # Buzzwords/adjectives
    'detail','detailed','detail-oriented','results','results-oriented','result','result-driven','driven',
    'motivated','self-motivated','hardworking','dedicated','passionate','innovative','creative','dynamic',
    'flexible','adaptable','proactive','strong','excellent','outstanding','proven','exceptional','extensive',
    'multiple','several','numerous','various','effective','efficient','fast','quick','robust','scalable',
    'best','top','highly','solid','deep','broad','team','teamwork','team-player','team-oriented','collaborative',
    'cross-functional','communication','communicator','interpersonal','presentation','presentations',
    'leadership','leader','mentorship','mentored','mentoring',

    # Low value verbs
    'use','used','using','make','makes','made','making','get','gets','got','getting','put','puts','putting',
    'set','sets','setting','include','includes','including','included','implement','implemented','implementing',
    'create','created','creating','build','built','building','develop','developed','developing','perform',
    'performed','performing','conduct','conducted','conducting','apply','applied','applying','execute',
    'executed','executing','ensure','ensured','ensuring','achieve','achieved','achieving','provide',
    'provided','providing','handle','handled','handling','train','trained','training','analyze','analyzed',
    'analyzing','prepare','prepared','preparing','plan','planned','planning','improve','improved','improving',
    'increase','increased','increasing','reduce','reduced','reducing','test','tested','testing','document',
    'documented','documenting','report','reported','reporting'
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