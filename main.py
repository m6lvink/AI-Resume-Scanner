'''
AI Resume Scanner - CLI Version utalizing Google API
Author: MK
'''
import sys
import os
import fitz  # PyMuPDF
import requests
import re
import json
from bs4 import BeautifulSoup
from ai_scanner import scan_resume_with_ai, list_available_models

# Try to import the secret key
try:
    import secrets_config
except ImportError:
    print("\n   !! CRITICAL ERROR: 'secrets_config.py' not found.")
    print("   !! Please rename 'secrets_config.example.py' to 'secrets_config.py' and add your API key.\n")
    sys.exit(1)

# --- UI HELPER FUNCTIONS ---

def clearScreen():
    # Function to clear the terminal screen for a fresh look
    os.system('cls' if os.name == 'nt' else 'clear')

def printHeader():
    # ASCII Art Header - Fixed Width (76 chars)
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
    # Function to print a header
    # Format: __ [ TITLE ] ____
    
    targetWidth = 76
    label = f" [ {title.upper()} ] "
    
    # Calculate padding: Width - length of "__" (2) - length of label
    paddingNeeded = targetWidth - 2 - len(label)
    
    # Safety check if title is too long
    if paddingNeeded < 0: 
        paddingNeeded = 0
        
    padding = "_" * paddingNeeded
    print(f"\n__{label}{padding}")

def printSuccess(text):
    print(f"   [+] {text}")

def printError(text):
    print(f"   [!] {text}")

def printInfo(text):
    print(f"   // {text}")


# --- CORE FUNCTIONS ---
def getPdfText(filePath):
    # Function to extract text from PDF
    if filePath is None:
        return ""

    try:
        doc = fitz.open(filePath)
        textParts = []
        
        for page in doc:
            text = page.get_text()
            textParts.append(text)
        
        doc.close()
        return "\n".join(textParts)
    except Exception:
        return ""

def getWebText(targetUrl):
    # Function to scrape text 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(targetUrl, headers=headers)
        if response.status_code != 200:
            return None

        soupObject = BeautifulSoup(response.text, 'html.parser')
        
        # Remove clutter
        badTags = ["script", "style", "nav", "footer", "header", "form", "button"]
        for tag in soupObject(badTags):
            tag.decompose()

        cleanText = soupObject.get_text(separator=' ')
        cleanText = re.sub(r'\s+', ' ', cleanText).strip()
        
        return cleanText

    except Exception:
        return None

def main():
    isProgramRunning = True
    
    # Initial Validation
    if "YOUR_API_KEY" in secrets_config.GOOGLE_API_KEY or "PASTE_YOUR_REAL" in secrets_config.GOOGLE_API_KEY:
        printError("You have not updated 'secrets_config.py' with your real Google API key.")
        return

    # Clear screen once at start
    clearScreen()
    printHeader()

    while isProgramRunning:
        printSection("INPUT DATA")
        
        jobUrl = input("\n   >> Enter Job Posting URL: ").strip()
        
        if len(jobUrl) == 0:
            printError("URL cannot be empty.")
            continue

        printInfo("Scraping Job Description...")
        jobDescription = getWebText(jobUrl)
        
        if jobDescription is None:
            printError("Failed to read URL.")
            continue

        resumePath = input("   >> Enter path to Resume PDF: ").strip()
        resumeContent = getPdfText(resumePath)
            
        if len(resumeContent) < 10:
            printError("Resume PDF is empty or invalid.")
            continue

        printInfo("Connecting to Neural Net...")
        
        # Calls the function from 'ai_scanner.py'
        aiResultJson = scan_resume_with_ai(secrets_config.GOOGLE_API_KEY, jobDescription, resumeContent)
        
        if aiResultJson:
            try:
                dataMap = json.loads(aiResultJson)
                
                score = dataMap.get("match_score", 0)
                missing = dataMap.get("missing_hard_skills", [])
                analysis = dataMap.get("strategic_analysis", "No analysis provided.")
                plan = dataMap.get("improvement_plan", [])
                
                # --- RESULTS DISPLAY ---
                
                # Score Bar
                # [=============                  ] 45%
                # The bar itself is 30 chars wide
                barLength = 30
                filledLength = int(barLength * score / 100)
                bar = '=' * filledLength + ' ' * (barLength - filledLength)
                
                printSection("MATCH RESULTS")
                print(f"\n   SCORE: [{bar}] {score}%")
                
                printSection("ANALYSIS")
                print(f"   // {analysis}")

                printSection("MISSING CRITICAL SKILLS")
                if len(missing) > 0:
                    for skill in missing:
                        print(f"   [x] {skill}")
                else:
                    printSuccess("No major hard skills missing. Clean sheet.")

                printSection("IMPROVEMENT PLAN")
                if len(plan) > 0:
                    for step in plan:
                        print(f"   -> {step}")
                else:
                    printSuccess("Resume is fully optimized for this role.")
                    
            except json.JSONDecodeError:
                printError("Neural Net returned invalid JSON.")
        else:
            printError("Neural Net failed to respond.")
            printInfo("Available Models for your key:")
            print(list_available_models(secrets_config.GOOGLE_API_KEY))

        print("\n// ============================================================== //")
        
        userChoice = input("\n   >> Analyze another? (y/n): ").lower()
        if userChoice != "y":
            isProgramRunning = False
            print("\n   // SYSTEM SHUTDOWN //")
        else:
            # Clear screen for next round to keep it fresh
            clearScreen()
            printHeader()

if __name__ == "__main__":
    main()