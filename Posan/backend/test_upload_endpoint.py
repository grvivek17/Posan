"""
Test the PDF upload endpoint directly
"""
import requests
import os
from pathlib import Path

# Backend URL
BACKEND_URL = "http://localhost:8000"
API_ENDPOINT = "/api/v1/ai/study-material/upload"

# PDF file path
pdf_path = Path(__file__).parent / "studydata" / "GR3MATHPA4SRM.pdf"

print(f"Testing PDF upload endpoint")
print(f"PDF file: {pdf_path}")
print(f"File exists: {pdf_path.exists()}")
print(f"File size: {pdf_path.stat().st_size / 1024:.2f} KB")

# Prepare the upload
with open(pdf_path, 'rb') as f:
    files = {'file': ('GR3MATHPA4SRM.pdf', f, 'application/pdf')}
    params = {'age_group': '9-11'}
    
    print(f"\nSending request to {BACKEND_URL}{API_ENDPOINT}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}{API_ENDPOINT}",
            files=files,
            params=params,
            timeout=120  # 2 minutes timeout for large PDFs
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS!")
            result = response.json()
            print(f"\nResponse Data:")
            print(f"  - Filename: {result.get('filename')}")
            print(f"  - Characters Extracted: {result.get('characters_extracted')}")
            print(f"  - Summary Length: {len(result.get('summary', ''))}")
            print(f"  - Key Topics: {result.get('key_topics', [])}")
        else:
            print(f"\n❌ ERROR!")
            print(f"Response Text: {response.text}")
            
            try:
                error_data = response.json()
                print(f"Error Details: {error_data}")
            except:
                pass
                
    except requests.exceptions.Timeout:
        print("\n❌ Request timeout! The PDF is taking too long to process.")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error! Is the backend running on http://localhost:8000?")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
