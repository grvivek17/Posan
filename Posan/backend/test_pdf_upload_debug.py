"""
Comprehensive test script for PDF upload and study material analysis.
This will help diagnose any issues with the PDF processing pipeline.
"""
import requests
import os
from reportlab.pdfgen import canvas

# Test 1: Create a simple PDF with text
def create_test_pdf(filename="test_study.pdf"):
    """Create a simple PDF with educational content."""
    c = canvas.Canvas(filename)
    c.setFont("Helvetica", 12)
    
    # Add educational content
    y = 750
    content = [
        "CHAPTER 1: PHOTOSYNTHESIS",
        "",
        "Photosynthesis is the process by which green plants and some other organisms",
        "use sunlight to synthesize foods with the help of chlorophyll pigments.",
        "",
        "In plants, photosynthesis generally takes place in leaves, which consist of",
        "chloroplasts. The process involves the intake of carbon dioxide and water,",
        "and the release of oxygen as a byproduct.",
        "",
        "Key Concepts:",
        "- Chlorophyll captures sunlight",
        "- Carbon dioxide + Water → Glucose + Oxygen",
        "- Occurs in chloroplasts",
        "- Essential for life on Earth",
        "",
        "The chemical equation for photosynthesis is:",
        "6CO2 + 6H2O + light energy → C6H12O6 + 6O2"
    ]
    
    for line in content:
        c.drawString(50, y, line)
        y -= 18
    
    c.save()
    print(f"✅ Created test PDF: {filename}")
    return filename

# Test 2: Upload the PDF via API
def test_upload(pdf_path):
    """Test uploading PDF to the study material endpoint."""
    url = "http://localhost:8000/api/v1/ai/study-material/upload"
    params = {"age_group": "9-11"}
    
    print(f"\n📤 Testing upload to: {url}")
    print(f"   PDF file: {pdf_path}")
    print(f"   File size: {os.path.getsize(pdf_path)} bytes")
    
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path, f, "application/pdf")}
            response = requests.post(url, params=params, files=files, timeout=60)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            print(f"\n📄 Response Data:")
            print(f"   Success: {data.get('success')}")
            print(f"   Filename: {data.get('filename')}")
            print(f"   Characters extracted: {data.get('characters_extracted')}")
            print(f"   Age group: {data.get('age_group')}")
            print(f"   Key topics count: {len(data.get('key_topics', []))}")
            print(f"\n📝 Summary preview:")
            summary = data.get('summary', '')
            print(f"   {summary[:200]}...")
            print(f"\n🎯 Key Topics:")
            for i, topic in enumerate(data.get('key_topics', []), 1):
                print(f"   {i}. {topic}")
            return True
        else:
            print(f"❌ FAILED!")
            print(f"\n📋 Error Details:")
            try:
                error_data = response.json()
                print(f"   {error_data}")
            except:
                print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend server!")
        print("   Make sure the backend is running at http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        return False

# Test 3: Verify PDF extraction locally
def test_local_extraction(pdf_path):
    """Test PDF text extraction using the same methods as the backend."""
    print(f"\n🔍 Testing local PDF extraction...")
    
    # Test 1: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        print(f"✅ pdfplumber: Extracted {len(text)} characters")
        print(f"   Preview: {text[:100]}...")
    except Exception as e:
        print(f"❌ pdfplumber failed: {e}")
    
    # Test 2: pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        print(f"✅ pypdf: Extracted {len(text)} characters")
        print(f"   Preview: {text[:100]}...")
    except Exception as e:
        print(f"❌ pypdf failed: {e}")
    
    # Test 3: fitz (PyMuPDF)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() or ""
        print(f"✅ fitz (PyMuPDF): Extracted {len(text)} characters")
        print(f"   Preview: {text[:100]}...")
    except Exception as e:
        print(f"❌ fitz failed: {e}")

# Main test runner
def main():
    print("="*70)
    print("   PDF UPLOAD AND STUDY MATERIAL ANALYSIS - DIAGNOSTIC TEST")
    print("="*70)
    
    # Create test PDF
    pdf_file = create_test_pdf()
    
    # Test local extraction
    test_local_extraction(pdf_file)
    
    # Test API upload
    success = test_upload(pdf_file)
    
    # Cleanup
    if os.path.exists(pdf_file):
        os.remove(pdf_file)
        print(f"\n🗑️  Cleaned up test file: {pdf_file}")
    
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED - Check errors above")
    print("="*70)

if __name__ == "__main__":
    main()
