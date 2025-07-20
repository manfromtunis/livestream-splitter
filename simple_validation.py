#!/usr/bin/env python3
"""
Simple validation script that doesn't require external dependencies
"""

import sys
import ast
from pathlib import Path

def test_python_syntax():
    """Test that all Python files have valid syntax"""
    print("🔍 Testing Python syntax...")
    
    python_files = [
        "src/stream_splitter/__init__.py",
        "src/stream_splitter/cli.py",
        "src/stream_splitter/config.py", 
        "src/stream_splitter/splitter.py",
        "src/stream_splitter/video_processor.py",
        "src/stream_splitter/utils.py"
    ]
    
    errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            ast.parse(source)
            print(f"✅ {file_path}")
        except SyntaxError as e:
            errors.append(f"{file_path}: {e}")
            print(f"❌ {file_path}: {e}")
    
    if errors:
        return False
    else:
        print("✅ All Python files have valid syntax")
        return True

def test_imports_structure():
    """Test import statements are correctly structured"""
    print("\n🔍 Testing import structure...")
    
    # Check that main modules have expected classes/functions
    checks = {
        "src/stream_splitter/config.py": ["class Config", "class OutputConfig", "class ProcessingConfig"],
        "src/stream_splitter/utils.py": ["def format_duration", "def sanitize_filename", "def parse_time_string"],
        "src/stream_splitter/cli.py": ["@click.command", "def main"],
        "src/stream_splitter/splitter.py": ["class Splitter"],
        "src/stream_splitter/video_processor.py": ["class VideoProcessor"]
    }
    
    errors = []
    for file_path, expected in checks.items():
        try:
            content = Path(file_path).read_text()
            for item in expected:
                if item not in content:
                    errors.append(f"{file_path} missing: {item}")
                else:
                    print(f"✅ Found {item} in {file_path}")
        except Exception as e:
            errors.append(f"Error reading {file_path}: {e}")
    
    if errors:
        for error in errors:
            print(f"❌ {error}")
        return False
    else:
        print("✅ All expected classes and functions found")
        return True

def test_requirements():
    """Test requirements.txt has expected dependencies"""
    print("\n🔍 Testing requirements.txt...")
    
    try:
        requirements = Path("requirements.txt").read_text()
        expected_deps = ["click", "ffmpeg-python", "pydantic", "pyyaml", "tqdm"]
        
        missing = []
        for dep in expected_deps:
            if dep not in requirements.lower():
                missing.append(dep)
            else:
                print(f"✅ Found {dep}")
        
        if missing:
            print(f"❌ Missing dependencies: {missing}")
            return False
        else:
            print("✅ All required dependencies listed")
            return True
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_documentation():
    """Test that key documentation exists"""
    print("\n🔍 Testing documentation...")
    
    doc_checks = {
        "README.md": ["## ✨ Features", "## 🚀 Quick Start", "### Installation"],
        "setup.py": ["entry_points", "install_requires", "console_scripts"]
    }
    
    errors = []
    for file_path, expected in doc_checks.items():
        try:
            content = Path(file_path).read_text()
            for item in expected:
                if item not in content:
                    errors.append(f"{file_path} missing: {item}")
                else:
                    print(f"✅ Found '{item}' in {file_path}")
        except Exception as e:
            errors.append(f"Error reading {file_path}: {e}")
    
    if errors:
        for error in errors:
            print(f"❌ {error}")
        return False
    else:
        print("✅ Documentation looks complete")
        return True

def main():
    """Run basic validation tests"""
    print("🚀 Simple Livestream Splitter Validation\n")
    
    tests = [
        ("Python Syntax", test_python_syntax),
        ("Import Structure", test_imports_structure), 
        ("Requirements", test_requirements),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print("🏁 VALIDATION SUMMARY")
    print('='*50)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 BASIC VALIDATION PASSED!")
        print("\n📋 To fully test the application:")
        print("1. Install FFmpeg on your system")
        print("2. Create a Python virtual environment:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("3. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("4. Install the package:")
        print("   pip install -e .")
        print("5. Test with a real video file:")
        print("   stream-splitter test_video.mp4 -o segments/ -l 5m")
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()