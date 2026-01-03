"""
Test script to read PDF from studydata folder and verify the flow
"""
import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_pdf_reading():
    """Test reading PDF files from studydata folder"""
    
    studydata_path = Path(__file__).parent / "studydata"
    
    print(f"📁 Checking studydata folder: {studydata_path}")
    print(f"Folder exists: {studydata_path.exists()}")
    
    if not studydata_path.exists():
        print("❌ studydata folder does not exist!")
        return False
    
    # List all PDF files
    pdf_files = list(studydata_path.glob("*.pdf"))
    print(f"\n📄 Found {len(pdf_files)} PDF file(s):")
    
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name} ({pdf_file.stat().st_size / 1024:.2f} KB)")
    
    if not pdf_files:
        print("❌ No PDF files found in studydata folder!")
        return False
    
    # Test reading the first PDF
    test_pdf = pdf_files[0]
    print(f"\n🔍 Testing PDF reading: {test_pdf.name}")
    
    try:
        # Try using PyPDF2
        try:
            from PyPDF2 import PdfReader
            print("✅ PyPDF2 is available")
            
            reader = PdfReader(str(test_pdf))
            num_pages = len(reader.pages)
            print(f"  📖 Number of pages: {num_pages}")
            
            # Extract text from first page
            if num_pages > 0:
                first_page = reader.pages[0]
                text = first_page.extract_text()
                print(f"  📝 First page text length: {len(text)} characters")
                print(f"  Preview (first 200 chars):")
                # Safe print with encoding handling
                preview_text = text[:200].encode('ascii', errors='ignore').decode('ascii')
                print(f"  {preview_text}...")
                
        except ImportError:
            print("⚠️ PyPDF2 not installed, trying pdfplumber...")
            
            try:
                import pdfplumber
                print("✅ pdfplumber is available")
                
                with pdfplumber.open(str(test_pdf)) as pdf:
                    num_pages = len(pdf.pages)
                    print(f"  📖 Number of pages: {num_pages}")
                    
                    if num_pages > 0:
                        first_page = pdf.pages[0]
                        text = first_page.extract_text()
                        print(f"  📝 First page text length: {len(text)} characters")
                        print(f"  Preview (first 200 chars):")
                        # Safe print with encoding handling
                        preview_text = text[:200].encode('ascii', errors='ignore').decode('ascii')
                        print(f"  {preview_text}...")
                        
            except ImportError:
                print("❌ Neither PyPDF2 nor pdfplumber is installed!")
                print("Install with: pip install PyPDF2 or pip install pdfplumber")
                return False
        
        print("\n✅ PDF reading test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error reading PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_file_permissions():
    """Test if we have proper read/write permissions"""
    
    studydata_path = Path(__file__).parent / "studydata"
    
    print("\n🔐 Testing file permissions...")
    
    # Test write permission
    test_file = studydata_path / "test_write.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test write permission")
        print("✅ Write permission: OK")
        
        # Clean up
        if test_file.exists():
            test_file.unlink()
            
    except Exception as e:
        print(f"❌ Write permission error: {str(e)}")
        return False
    
    # Test read permission on PDF
    pdf_files = list(studydata_path.glob("*.pdf"))
    if pdf_files:
        try:
            with open(pdf_files[0], 'rb') as f:
                f.read(100)  # Read first 100 bytes
            print("✅ Read permission: OK")
        except Exception as e:
            print(f"❌ Read permission error: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("PDF Reading Test for Study Assistant")
    print("=" * 60)
    
    # Test file permissions first
    if not test_file_permissions():
        print("\n❌ Permission test failed!")
        sys.exit(1)
    
    # Test PDF reading
    if not test_pdf_reading():
        print("\n❌ PDF reading test failed!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
