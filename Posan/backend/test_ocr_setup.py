"""
Quick test script to verify Tesseract OCR is working correctly.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import ocr_service

def test_tesseract():
    """Test if Tesseract is properly configured."""
    print("🔍 Testing Tesseract OCR Installation...\n")
    
    try:
        import pytesseract
        print(f"✅ pytesseract imported successfully")
        print(f"   Version: {pytesseract.__version__}")
        
        # Try to get Tesseract version
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract OCR found!")
            print(f"   Version: {version}")
        except Exception as e:
            print(f"❌ Tesseract not accessible: {e}")
            return False
        
        print(f"\n✅ OCR Service initialized successfully!")
        print(f"   Tesseract command: {pytesseract.pytesseract.tesseract_cmd}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_tesseract()
    
    if success:
        print("\n" + "="*50)
        print("✅ All OCR components are working correctly!")
        print("="*50)
        print("\n📝 You can now upload test papers and they will be")
        print("   processed with Tesseract OCR.")
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("❌ OCR setup incomplete")
        print("="*50)
        print("\n📝 Please check TESSERACT_OCR_SETUP.md for installation instructions.")
        sys.exit(1)
