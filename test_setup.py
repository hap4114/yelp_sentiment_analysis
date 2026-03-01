"""
Quick setup verification script.
Run this before starting the Streamlit app to ensure everything is configured correctly.
"""

import os
import sys

def check_dependencies():
    """Check if all required packages are installed."""
    print("="*60)
    print("1. CHECKING DEPENDENCIES")
    print("="*60)
    
    required_packages = [
        'streamlit',
        'pandas',
        'google.generativeai',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('.', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print("\n⚠️  Missing packages detected!")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed!")
    return True


def check_api_key():
    """Check if Gemini API key is configured."""
    print("\n" + "="*60)
    print("2. CHECKING API KEYS")
    print("="*60)
    
    # Try loading from .env
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    all_present = True
    
    # Check Gemini
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in environment")
        all_present = False
    elif gemini_key == "your_gemini_api_key_here":
        print("❌ Please replace the placeholder Gemini API key")
        all_present = False
    else:
        print(f"✅ Gemini API Key: {gemini_key[:10]}...{gemini_key[-4:]}")
    
    # Check Supabase (optional)
    if not supabase_url or not supabase_key:
        print("⚠️  Supabase credentials not found (will use CSV fallback)")
        print("   Recommended: Set up Supabase for production")
    elif supabase_url == "your_supabase_project_url_here":
        print("⚠️  Supabase URL is placeholder (will use CSV fallback)")
    else:
        print(f"✅ Supabase URL: {supabase_url}")
        print(f"✅ Supabase Key: {supabase_key[:20]}...{supabase_key[-4:]}")
    
    if not all_present:
        print("\n📝 Setup instructions:")
        print("1. Copy .env.example to .env")
        print("2. Get Gemini key: https://makersuite.google.com/app/apikey")
        print("3. (Optional) Setup Supabase: See SUPABASE_SETUP.md")
        print("4. Add keys to .env file")
    
    return all_present


def test_gemini_connection():
    """Test actual connection to Gemini API."""
    print("\n" + "="*60)
    print("3. TESTING GEMINI CONNECTION")
    print("="*60)
    
    try:
        from llm_client import test_gemini_connection
        success = test_gemini_connection()
        return success
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False


def check_file_structure():
    """Verify all required files exist."""
    print("\n" + "="*60)
    print("4. CHECKING FILE STRUCTURE")
    print("="*60)
    
    required_files = [
        'app.py',
        'llm_client.py',
        'prompts.py',
        'utils.py',
        'requirements.txt',
        '.env.example'
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_present = False
    
    if all_present:
        print("\n✅ All required files present!")
    else:
        print("\n⚠️  Some files are missing!")
    
    return all_present


def initialize_storage():
    """Initialize both CSV and Supabase storage."""
    print("\n" + "="*60)
    print("5. INITIALIZING STORAGE")
    print("="*60)
    
    try:
        from utils import init_storage
        init_storage()
        return True
    except Exception as e:
        print(f"❌ Error initializing storage: {e}")
        return False


def run_all_checks():
    """Run all verification checks."""
    print("\n")
    print("🔍 SETUP VERIFICATION SCRIPT")
    print("="*60)
    print()
    
    results = {
        "dependencies": check_dependencies(),
        "api_key": check_api_key(),
        "files": check_file_structure(),
        "storage": initialize_storage()
    }
    
    # Only test connection if API key is present
    if results["api_key"]:
        results["connection"] = test_gemini_connection()
    else:
        results["connection"] = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check.replace('_', ' ').title()}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("\nYou're ready to run the app:")
        print("  streamlit run app.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the app.")
    
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)