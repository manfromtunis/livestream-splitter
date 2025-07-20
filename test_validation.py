#!/usr/bin/env python3
"""
Validation script for Livestream Splitter
Tests code structure, imports, and basic functionality without external dependencies
"""

import sys
import os
import importlib.util
from pathlib import Path

def test_project_structure():
    """Test that all required files and directories exist"""
    print("🔍 Testing project structure...")
    
    required_files = [
        "src/stream_splitter/__init__.py",
        "src/stream_splitter/cli.py", 
        "src/stream_splitter/config.py",
        "src/stream_splitter/splitter.py",
        "src/stream_splitter/video_processor.py",
        "src/stream_splitter/utils.py",
        "requirements.txt",
        "setup.py",
        "README.md",
        "config/default_config.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_imports():
    """Test that all modules can be imported (without external deps)"""
    print("\n🔍 Testing module imports...")
    
    # Add src to path
    sys.path.insert(0, str(Path("src").resolve()))
    
    try:
        # Test basic imports
        from stream_splitter import __version__
        print(f"✅ Package version: {__version__}")
        
        # Test config module
        from stream_splitter.config import Config, OutputConfig, IntroOutroConfig, ProcessingConfig
        print("✅ Config classes imported successfully")
        
        # Test utils module
        from stream_splitter.utils import format_duration, sanitize_filename, parse_time_string
        print("✅ Utility functions imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_utility_functions():
    """Test utility functions with sample data"""
    print("\n🔍 Testing utility functions...")
    
    sys.path.insert(0, str(Path("src").resolve()))
    
    try:
        from stream_splitter.utils import format_duration, sanitize_filename, parse_time_string
        
        # Test format_duration
        assert format_duration(30) == "30s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3661) == "1h 1m 1s"
        print("✅ format_duration working correctly")
        
        # Test sanitize_filename
        assert sanitize_filename("test<>file") == "test__file"
        assert sanitize_filename("file with spaces") == "file_with_spaces"
        assert sanitize_filename("") == "unnamed"
        print("✅ sanitize_filename working correctly")
        
        # Test parse_time_string
        assert parse_time_string("120") == 120
        assert parse_time_string("2m") == 120
        assert parse_time_string("1h30m") == 5400
        print("✅ parse_time_string working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Utility function test failed: {e}")
        return False

def test_config_validation():
    """Test configuration system without file dependencies"""
    print("\n🔍 Testing configuration system...")
    
    sys.path.insert(0, str(Path("src").resolve()))
    
    try:
        from stream_splitter.config import OutputConfig, ProcessingConfig
        
        # Test valid config
        output_config = OutputConfig(
            directory=Path("./test_segments"),
            max_segment_length=1200
        )
        assert output_config.max_segment_length == 1200
        print("✅ OutputConfig validation working")
        
        # Test processing config
        proc_config = ProcessingConfig(
            quality="high",
            threads=4
        )
        assert proc_config.quality == "high"
        assert proc_config.threads == 4
        print("✅ ProcessingConfig validation working")
        
        # Test invalid segment length
        try:
            OutputConfig(max_segment_length=30)  # Too short
            print("❌ Should have failed validation")
            return False
        except Exception:
            print("✅ Validation correctly rejected invalid segment length")
        
        return True
        
    except Exception as e:
        print(f"❌ Config validation test failed: {e}")
        return False

def test_cli_structure():
    """Test CLI module structure"""
    print("\n🔍 Testing CLI structure...")
    
    sys.path.insert(0, str(Path("src").resolve()))
    
    try:
        # Read CLI file to check for key components
        cli_file = Path("src/stream_splitter/cli.py").read_text()
        
        required_elements = [
            "@click.command()",
            "def main(",
            "--output-dir",
            "--max-length",
            "--intro",
            "--outro"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in cli_file:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing CLI elements: {missing_elements}")
            return False
        else:
            print("✅ CLI structure looks correct")
            return True
            
    except Exception as e:
        print(f"❌ CLI structure test failed: {e}")
        return False

def test_setup_py():
    """Test setup.py configuration"""
    print("\n🔍 Testing setup.py...")
    
    try:
        setup_content = Path("setup.py").read_text()
        
        required_fields = [
            "name=\"livestream-splitter\"",
            "version=\"0.1.0\"",
            "install_requires=",
            "entry_points=",
            "stream-splitter=stream_splitter.cli:main"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in setup_content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing setup.py fields: {missing_fields}")
            return False
        else:
            print("✅ setup.py configuration looks correct")
            return True
            
    except Exception as e:
        print(f"❌ setup.py test failed: {e}")
        return False

def create_mock_test_files():
    """Create mock files for testing without actual video processing"""
    print("\n🔍 Creating mock test environment...")
    
    try:
        # Create test directory
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)
        
        # Create a fake video file for testing (just a text file)
        fake_video = test_dir / "test_video.mp4"
        fake_video.write_text("This is a fake video file for testing")
        
        # Create fake intro/outro
        fake_intro = test_dir / "intro.mp4"
        fake_intro.write_text("Fake intro video")
        
        fake_outro = test_dir / "outro.mp4"
        fake_outro.write_text("Fake outro video")
        
        print("✅ Mock test files created")
        return True, test_dir
        
    except Exception as e:
        print(f"❌ Failed to create mock files: {e}")
        return False, None

def test_configuration_files():
    """Test configuration file formats"""
    print("\n🔍 Testing configuration files...")
    
    try:
        import yaml
        
        # Test default config
        with open("config/default_config.yaml", 'r') as f:
            config_data = yaml.safe_load(f)
        
        required_sections = ['output', 'intro_outro', 'processing']
        for section in required_sections:
            if section not in config_data:
                print(f"❌ Missing config section: {section}")
                return False
        
        print("✅ Configuration files are valid YAML")
        return True
        
    except ImportError:
        print("⚠️ PyYAML not available, skipping YAML validation")
        return True
    except Exception as e:
        print(f"❌ Configuration file test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 Starting Livestream Splitter Validation\n")
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Module Imports", test_imports),
        ("Utility Functions", test_utility_functions),
        ("Configuration Validation", test_config_validation),
        ("CLI Structure", test_cli_structure),
        ("Setup.py", test_setup_py),
        ("Configuration Files", test_configuration_files),
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
        print("\n🎉 ALL TESTS PASSED! The project structure is correct.")
        print("\n📝 Next steps:")
        print("1. Install FFmpeg: https://ffmpeg.org/download.html")
        print("2. Install Python dependencies: pip install -r requirements.txt")
        print("3. Install the package: pip install -e .")
        print("4. Test with real video files")
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)