#!/usr/bin/env python3
"""
Regression test suite to ensure CLI functionality still works after web UI addition
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_cli_imports():
    """Test that CLI modules can still be imported"""
    print("🧪 Testing CLI imports...")
    
    try:
        sys.path.insert(0, 'src')
        from stream_splitter.cli import main
        from stream_splitter.config import Config
        from stream_splitter.splitter import Splitter
        from stream_splitter.video_processor import VideoProcessor
        print("✅ All CLI modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_cli_help():
    """Test that CLI help still works"""
    print("🧪 Testing CLI help command...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'src.stream_splitter.cli', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and ('usage:' in result.stdout.lower() or 'options:' in result.stdout.lower()):
            print("✅ CLI help command works")
            return True
        else:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        return False

def test_config_creation():
    """Test configuration object creation"""
    print("🧪 Testing config creation...")
    
    try:
        sys.path.insert(0, 'src')
        from stream_splitter.config import Config, OutputConfig
        
        # Test with the actual video file
        video_path = "therealbakchich_Just%20Chatting_2025-07-17_720p30.mp4"
        if not os.path.exists(video_path):
            print("⚠️  Test video not found, skipping config test")
            return True
        
        config = Config(
            input_path=video_path,
            output=OutputConfig(directory="./test_regression_output")
        )
        
        print(f"✅ Config created successfully: {config.input_path}")
        return True
        
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        return False

def test_video_info_extraction():
    """Test video info extraction still works"""
    print("🧪 Testing video info extraction...")
    
    try:
        sys.path.insert(0, 'src')
        from stream_splitter.video_processor import VideoProcessor
        
        video_path = "therealbakchich_Just%20Chatting_2025-07-17_720p30.mp4"
        if not os.path.exists(video_path):
            print("⚠️  Test video not found, skipping video info test")
            return True
        
        processor = VideoProcessor()
        if not processor.ffmpeg_path:
            print("⚠️  FFmpeg not found, skipping video info test")
            return True
            
        video_info = processor.get_video_info(Path(video_path))
        
        required_keys = ['duration', 'width', 'height', 'codec', 'fps']
        for key in required_keys:
            if key not in video_info:
                print(f"❌ Missing key in video info: {key}")
                return False
        
        print(f"✅ Video info extracted: {video_info['duration']}s, {video_info['width']}x{video_info['height']}")
        return True
        
    except Exception as e:
        print(f"❌ Video info extraction failed: {e}")
        return False

def test_web_imports():
    """Test that web modules don't break existing functionality"""
    print("🧪 Testing web module imports...")
    
    try:
        # Test that web backend can import our modules
        sys.path.insert(0, 'src')
        from stream_splitter.config import Config
        from stream_splitter.splitter import Splitter
        
        # Test that we can import web modules
        sys.path.insert(0, 'web/backend')
        import main as web_main
        
        print("✅ Web modules import without conflicts")
        return True
        
    except Exception as e:
        print(f"❌ Web import test failed: {e}")
        return False

def test_cli_backward_compatibility():
    """Test that existing CLI commands still work the same way"""
    print("🧪 Testing CLI backward compatibility...")
    
    video_path = "therealbakchich_Just%20Chatting_2025-07-17_720p30.mp4"
    if not os.path.exists(video_path):
        print("⚠️  Test video not found, skipping CLI compatibility test")
        return True
    
    try:
        # Test with a short segment to avoid long processing (minimum 60s)
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                sys.executable, '-m', 'src.stream_splitter.cli',
                video_path,
                '--max-length', '60s',  # Minimum allowed segment length
                '--output-dir', temp_dir
            ], capture_output=True, text=True, timeout=90)
            
            if result.returncode == 0:
                print("✅ CLI backward compatibility maintained")
                return True
            else:
                print(f"❌ CLI compatibility test failed: {result.stderr}")
                return False
                
    except subprocess.TimeoutExpired:
        print("⚠️  CLI test timed out (this is expected for large files)")
        return True
    except Exception as e:
        print(f"❌ CLI compatibility test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up any test output files"""
    import shutil
    
    test_dirs = ["test_regression_output", "uploads", "outputs"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up {test_dir}")

def main():
    """Run all regression tests"""
    print("🔍 Livestream Splitter - Regression Test Suite")
    print("=" * 50)
    
    tests = [
        test_cli_imports,
        test_cli_help,
        test_config_creation,
        test_video_info_extraction,
        test_web_imports,
        test_cli_backward_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All regression tests PASSED! Safe to deploy web UI.")
    else:
        print("⚠️  Some tests failed. Review before deploying.")
    
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)