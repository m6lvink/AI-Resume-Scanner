import google.generativeai as genai
import time
import re
from google.api_core import exceptions as google_exceptions

def scanResumeWithAi(apiKey, jobText, resumeText):
    if not apiKey or not isinstance(apiKey, str) or len(apiKey.strip()) == 0:
        return None
    if not jobText or len(str(jobText).strip()) == 0:
        return None
    if not resumeText or len(str(resumeText).strip()) == 0:
        return None
    
    try:
        genai.configure(api_key=apiKey)
    except (ValueError, AttributeError):
        return None
    
    modelsToTry = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-2.0-flash',
        'gemini-2.0-flash-exp'
    ]
    
    systemPrompt = (
        "You are an expert Career Coach and Technical Recruiter utilizing an advanced ATS (Applicant Tracking System). "
        "Your goal is to maximize the candidate's chances of getting an interview.\n\n"
        
        "TASK:\n"
        "Analyze the provided Job Description against the Resume.\n"
        "Return the result strictly as a valid JSON object. Do not use Markdown formatting (no ```json blocks).\n\n"
        
        "JSON STRUCTURE:\n"
        "{\n"
        "  \"match_score\": <Integer 0-100>,\n"
        "  \"missing_hard_skills\": [<List of specific technical tools/languages missing>],\n"
        "  \"strategic_analysis\": \"<One sentence explaining WHY the score is what it is>\",\n"
        "  \"improvement_plan\": [\n"
        "     \"<Actionable Step 1: Specific keyword to add and where>\",\n"
        "     \"<Actionable Step 2: Specific experience to highlight or rephrase>\",\n"
        "     \"<Actionable Step 3: Formatting or structural advice if needed>\"\n"
        "  ]\n"
        "}\n\n"
        
        "SCORING RULES:\n"
        "1. IGNORE soft skills (e.g., 'team player', 'communication', 'passion'). These do not count for ATS scoring.\n"
        "2. FOCUS heavily on Hard Skills: Languages, Frameworks, Tools, Certifications, and specific Methodologies.\n"
        "3. SYNONYM AWARENESS: If the job asks for 'AWS' and resume has 'Amazon Web Services', count it as a match.\n"
        "4. IMPROVEMENT PLAN: Be specific. Don't just say 'Add more skills'. Say 'Explicitly mention experience with Docker in the Work History section'.\n"
    )
    
    fullPrompt = f"{systemPrompt}\n\n=== JOB DESCRIPTION ===\n{jobText}\n\n=== RESUME ===\n{resumeText}"

    for modelName in modelsToTry:
        try:
            aiModel = genai.GenerativeModel(modelName)
            response = aiModel.generate_content(fullPrompt)
            
            if hasattr(response, 'text') and response.text:
                cleanResponse = response.text.replace("```json", "").replace("```", "").strip()
                return cleanResponse

        except google_exceptions.ResourceExhausted as e:
            retryDelay = 15
            errorStr = str(e).lower()
            if "retry in" in errorStr:
                try:
                    match = re.search(r'retry in ([\d.]+)s', errorStr)
                    if match:
                        retryDelay = max(15, int(float(match.group(1))) + 2)
                except:
                    pass
            time.sleep(retryDelay)
            continue
        except (ValueError, AttributeError, TypeError, google_exceptions.GoogleAPIError):
            continue
            
    return None

def listAvailableModels(apiKey):
    if not apiKey or not isinstance(apiKey, str):
        return ["Invalid API key"]
    try:
        genai.configure(api_key=apiKey)
        available = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available.append(m.name)
        return available
    except (ValueError, AttributeError, Exception) as e:
        return [str(e)]