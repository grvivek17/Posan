"""
Test the PDF upload endpoint directly and save result
"""
import requests
import os
import json
from pathlib import Path

# Backend URL
BACKEND_URL = "http://localhost:8000"
API_ENDPOINT = "/api/v1/ai/study-material/upload"

# PDF file path
pdf_path = Path(__file__).parent / "studydata" / "GR3MATHPA4SRM.pdf"

print(f"Testing PDF upload endpoint")
print(f"File: {pdf_path}")

if not pdf_path.exists():
    print(f"Error: {pdf_path} not found")
    exit(1)

with open(pdf_path, 'rb') as f:
    files = {'file': ('GR3MATHPA4SRM.pdf', f, 'application/pdf')}
    params = {'age_group': '9-11'}
    
    print(f"Requesting: {BACKEND_URL}{API_ENDPOINT}")
    try:
        response = requests.post(
            f"{BACKEND_URL}{API_ENDPOINT}",
            files=files,
            params=params,
            timeout=180
        )
        
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text[:1000] # preview
        }
        
        if response.status_code == 200:
            result["json"] = response.json()
            print("Status: 200 OK")
        else:
            print(f"Status: {response.status_code}")
            
        with open("upload_test_result.json", "w") as out:
            json.dump(result, out, indent=2)
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        with open("upload_test_result.json", "w") as out:
            json.dump({"error": str(e)}, out, indent=2)
