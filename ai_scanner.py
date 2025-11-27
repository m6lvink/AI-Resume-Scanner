import google.generativeai as genai

def scan_resume_with_ai(api_key, job_text, resume_text):
    """
    Sends the job and resume text to Google Gemini for deep analysis.
    Returns a JSON string with score, missing skills, and improvement advice.
    """
    
    # Configure the Cloud AI
    genai.configure(api_key=api_key)
    
    # Priority list of models to attempt 
    models_to_try = [
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-2.0-flash-lite',
        'gemini-1.5-flash'
    ]
    
    # We ask for a "strategic_analysis" to explain the score and an "improvement_plan" for actionable steps.
    system_prompt = (
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
    
    full_prompt = f"{system_prompt}\n\n=== JOB DESCRIPTION ===\n{job_text}\n\n=== RESUME ===\n{resume_text}"

    # Try models in order of priority
    for model_name in models_to_try:
        try:
            ai_model = genai.GenerativeModel(model_name)
            response = ai_model.generate_content(full_prompt)
            
            # Clean potential markdown formatting
            clean_response = response.text.replace("```json", "").replace("```", "").strip()
            return clean_response

        except Exception:
            continue
            
    # If we get here, all models failed D:
    return None

def list_available_models(api_key):
    """Helper to debug model availability"""
    genai.configure(api_key=api_key)
    try:
        available = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available.append(m.name)
        return available
    except Exception as e:
        return [str(e)]