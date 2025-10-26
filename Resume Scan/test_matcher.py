#!/usr/bin/env python3
"""Test script to verify the matcher module works correctly."""

import sys

print("Testing imports...")
try:
    from matcher import getMatchScore, categorizeKeywords, loadModel
    print("✓ matcher imports successful")
except Exception as e:
    print(f"✗ matcher import failed: {e}")
    sys.exit(1)

try:
    from resumeParser import extractTextFromPdf
    print("✓ resumeParser import successful")
except Exception as e:
    print(f"✗ resumeParser import failed: {e}")
    sys.exit(1)

print("\nTesting model loading...")
try:
    model = loadModel()
    print(f"✓ Model loaded: {type(model)}")
except Exception as e:
    print(f"✗ Model load failed: {e}")
    sys.exit(1)

print("\nTesting scoring function...")
try:
    jobDesc = "Looking for a Python developer with Django and PostgreSQL experience. Must know Docker and AWS."
    resumeText = "Experienced Python developer. Worked with Django, Flask, PostgreSQL, MySQL. Familiar with Docker, Kubernetes, AWS, and Azure."
    
    score, matched, missing = getMatchScore(jobDesc, resumeText)
    print(f"✓ Score calculated: {score * 100:.1f}%")
    print(f"  Matched: {len(matched)} keywords")
    print(f"  Missing: {len(missing)} keywords")
except Exception as e:
    print(f"✗ Scoring failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting categorization...")
try:
    cats = categorizeKeywords(matched)
    print(f"✓ Categorization successful")
    print(f"  Languages: {len(cats['languages'])}")
    print(f"  Frameworks: {len(cats['frameworks'])}")
    print(f"  Tools: {len(cats['tools'])}")
    print(f"  Databases: {len(cats['databases'])}")
    print(f"  Other: {len(cats['other'])}")
except Exception as e:
    print(f"✗ Categorization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed!")
print("\nExample matched keywords:", sorted(list(matched))[:10])
print("Example missing keywords:", sorted(list(missing))[:10])