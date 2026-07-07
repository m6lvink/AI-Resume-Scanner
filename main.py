'''
AI Resume Scanner - CLI Version utilizing Google API
Author: MK
'''
import sys
import os
import fitz
import requests
import re
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from ai_scanner import scanResumeWithAi, listAvailableModels

load_dotenv()

googleApiKey = os.getenv('GOOGLE_API_KEY')
if not googleApiKey:
    print("\n!! ERROR: 'GOOGLE_API_KEY' not found in '.env' file.")
    print("!! Please copy '.env.example' to '.env' and add your API key.\n")
    sys.exit(1)

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def printHeader():
    header = r"""
// ========================================================================== //
//                                                                            //
//    ____  _____ _____ __  ____  __  _____    ____ _____ ___    _   __       //
//   / __ \/ ____/ ___/ / / /  |/  |/ ____/  / ___/ ____/   |  / | / /       //
//  / /_/ / __/  \__ \/ / / / /|_/ / __/     \__ \ /    / /| | /  |/ /        //
// / _, _/ /___ ___/ / /_/ / /  / / /___    ___/ / /___/ ___ |/ /|  /         //
///_/ |_/_____//____/\____/_/  /_/_____/   /____/\____/_/  |_/_/ |_/          //
//                                                                            //
//                        RESUME SCANNER by MK                                //
//                                                                            //
// ========================================================================== //
    """
    print(header.strip())

def printSection(title):
    targetWidth = 76
    label = f" [ {title.upper()} ] "
    paddingNeeded = targetWidth - 2 - len(label)
    if paddingNeeded < 0: 
        paddingNeeded = 0
    padding = "_" * paddingNeeded
    print(f"\n__{label}{padding}")

def printSuccess(text):
    print(f"[+] {text}")

def printError(text):
    print(f"[!] {text}")

def printInfo(text):
    print(f"// {text}")

def getPdfText(filePath):
    if filePath is None or not isinstance(filePath, str) or len(filePath.strip()) == 0:
        return ""
    filePath = os.path.normpath(os.path.expanduser(filePath.strip().strip('"').strip("'")))
    if not os.path.isfile(filePath) or os.path.isdir(filePath):
        return ""

    try:
        doc = fitz.open(filePath)
        textParts = []
        for page in doc:
            text = page.get_text()
            textParts.append(text)
        doc.close()
        return "\n".join(textParts)
    except (fitz.FileDataError, IOError, OSError):
        return ""

def getWebText(targetUrl):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        response = requests.get(targetUrl, headers=headers, timeout=30, allow_redirects=True)
        if response.status_code != 200:
            return None

        responseText = response.text.lower()
        verificationIndicators = [
            "captcha",
            "verify you are human",
            "please verify",
            "access denied",
            "blocked",
            "cloudflare",
            "checking your browser",
            "unusual traffic"
        ]
        
        for indicator in verificationIndicators:
            if indicator in responseText:
                return "VERIFICATION_REQUIRED"

        soupObject = BeautifulSoup(response.text, 'html.parser')
        badTags = ["script", "style", "nav", "footer", "header", "form", "button"]
        for tag in soupObject(badTags):
            tag.decompose()

        cleanText = soupObject.get_text(separator=' ')
        cleanText = re.sub(r'\s+', ' ', cleanText).strip()
        
        if len(cleanText) < 50:
            return "VERIFICATION_REQUIRED"
            
        return cleanText

    except requests.RequestException:
        return None

def main():
    isProgramRunning = True
    
    apiKeyStr = str(googleApiKey)
    if "YOUR_API_KEY" in apiKeyStr or "PASTE_YOUR_REAL" in apiKeyStr or len(apiKeyStr.strip()) < 20:
        printError("You have not updated '.env' with your real Google API key.")
        return

    clearScreen()
    printHeader()

    while isProgramRunning:
        printSection("INPUT DATA")
        
        jobUrl = input("\n>> Enter Job Posting URL: ").strip()
        
        if len(jobUrl) == 0:
            printError("URL cannot be empty.")
            continue
        if not jobUrl.startswith(('http://', 'https://')):
            printError("URL must start with http:// or https://")
            continue

        printInfo("Scraping Job Description...")
        jobDescription = getWebText(jobUrl)
        
        if jobDescription == "VERIFICATION_REQUIRED":
            printError("Website requires verification. Cannot scrape automatically.")
            printInfo("Please copy and paste the job description manually.")
            jobDescription = input("\n>> Paste job description (press Enter when done): ").strip()
            if len(jobDescription) < 50:
                printError("Job description too short. Please try again.")
                continue
        elif jobDescription is None or len(jobDescription.strip()) == 0:
            printError("Failed to read URL or URL returned empty content.")
            printInfo("You can paste the job description manually instead.")
            manualInput = input(">> Paste job description manually? (y/n): ").strip().lower()
            if manualInput == "y":
                jobDescription = input("\n>> Paste job description (press Enter when done): ").strip()
                if len(jobDescription) < 50:
                    printError("Job description too short. Please try again.")
                    continue
            else:
                continue

        resumePath = input(">> Enter path to Resume PDF: ").strip()
        if len(resumePath) == 0:
            printError("Resume path cannot be empty.")
            continue
        resumeContent = getPdfText(resumePath)
            
        if len(resumeContent) < 10:
            printError("Resume PDF is empty or invalid.")
            continue

        printInfo("Connecting to Neural Net...")
        
        aiResultJson = scanResumeWithAi(googleApiKey, jobDescription, resumeContent)
        
        if aiResultJson:
            try:
                dataMap = json.loads(aiResultJson)
                
                score = dataMap.get("match_score", 0)
                if not isinstance(score, (int, float)):
                    score = 0
                score = max(0, min(100, int(score)))
                
                missing = dataMap.get("missing_hard_skills", [])
                if not isinstance(missing, list):
                    missing = []
                
                analysis = dataMap.get("strategic_analysis", "No analysis provided.")
                if not isinstance(analysis, str):
                    analysis = "No analysis provided."
                
                plan = dataMap.get("improvement_plan", [])
                if not isinstance(plan, list):
                    plan = []
                
                barLength = 30
                filledLength = int(barLength * score / 100)
                bar = '=' * filledLength + ' ' * (barLength - filledLength)
                
                printSection("MATCH RESULTS")
                print(f"\nSCORE: [{bar}] {score}%")
                
                printSection("ANALYSIS")
                print(f"// {analysis}")

                printSection("MISSING CRITICAL SKILLS")
                if len(missing) > 0:
                    for skill in missing:
                        print(f"[x] {skill}")
                else:
                    printSuccess("No major hard skills missing. Clean sheet.")

                printSection("IMPROVEMENT PLAN")
                if len(plan) > 0:
                    for step in plan:
                        print(f"-> {step}")
                else:
                    printSuccess("Resume is fully optimized for this role.")
                    
            except json.JSONDecodeError:
                printError("Neural Net returned invalid JSON.")
        else:
            printError("Neural Net failed to respond.")
            printInfo("Available Models for your key:")
            print(listAvailableModels(googleApiKey))

        print("\n// ============================================================== //")
        
        userChoice = input("\n>> Analyze another? (y/n): ").strip().lower()
        if userChoice != "y":
            isProgramRunning = False
            print("\n// SYSTEM SHUTDOWN //")
        else:
            clearScreen()
            printHeader()

if __name__ == "__main__":
    main()
