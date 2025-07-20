# Testing Guide for Livestream Splitter

This guide helps you verify that the Livestream Splitter works correctly on your system.

## ✅ Quick Validation

Run the basic validation script to check the code structure:

```bash
python3 simple_validation.py
```

This will verify:
- ✅ Python syntax is correct
- ✅ All required classes and functions exist
- ✅ Dependencies are properly listed
- ✅ Documentation is complete

## 🔧 Full Installation & Testing

### 1. Prerequisites

**Install FFmpeg** (required for video processing):

- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg` 
- **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html)

**Verify FFmpeg installation**:
```bash
ffmpeg -version
```

### 2. Install Python Dependencies

**Create virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install dependencies**:
```bash
pip install -r requirements.txt
```

**Install the package**:
```bash
pip install -e .
```

### 3. Verify Installation

**Check if the command is available**:
```bash
stream-splitter --help
```

**Check FFmpeg integration**:
```bash
stream-splitter check-ffmpeg
```

**Check version**:
```bash
stream-splitter version
```

## 🧪 Test with Sample Videos

### Create Test Videos (if needed)

If you don't have test videos, create some using FFmpeg:

```bash
# Create a 2-minute test video
ffmpeg -f lavfi -i testsrc=duration=120:size=1280x720:rate=30 -c:v libx264 test_video.mp4

# Create a 5-second intro
ffmpeg -f lavfi -i testsrc=duration=5:size=1280x720:rate=30 -c:v libx264 intro.mp4

# Create a 3-second outro
ffmpeg -f lavfi -i testsrc=duration=3:size=1280x720:rate=30 -c:v libx264 outro.mp4
```

### Basic Tests

**Test 1: Simple splitting**
```bash
stream-splitter test_video.mp4 -o segments/ -l 30s
```
Expected: Creates 4 segments of ~30 seconds each

**Test 2: With custom naming**
```bash
stream-splitter test_video.mp4 -o segments/ -l 45s --naming-pattern "test_part{index:02d}"
```
Expected: Creates segments named `test_part01.mp4`, `test_part02.mp4`, etc.

**Test 3: With intro/outro**
```bash
stream-splitter test_video.mp4 --intro intro.mp4 --outro outro.mp4 -o segments/ -l 60s
```
Expected: Each segment has intro + content + outro

**Test 4: Different format**
```bash
stream-splitter test_video.mp4 -f mkv -o segments/ -l 30s
```
Expected: Creates MKV format segments

**Test 5: Using configuration file**
```bash
stream-splitter test_video.mp4 -c examples/batch_config.yaml
```
Expected: Uses settings from config file

### Advanced Tests

**Test 6: Quality settings**
```bash
stream-splitter test_video.mp4 --quality high --threads 4 -o segments/
```

**Test 7: Save configuration**
```bash
stream-splitter test_video.mp4 -l 90s --intro intro.mp4 --save-config my_preset.yaml
```

**Test 8: Verbose logging**
```bash
stream-splitter test_video.mp4 -v -o segments/
```

## 🔍 Troubleshooting Tests

### Common Issues

**"FFmpeg not found"**
```bash
# Test FFmpeg
which ffmpeg
ffmpeg -version

# If not found, install FFmpeg for your OS
```

**"No module named 'click'"**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"Permission denied"**
```bash
# Check write permissions
ls -la ./
mkdir test_segments  # Should succeed
```

**Memory issues with large files**
```bash
# Test with smaller segments
stream-splitter large_video.mp4 -l 5m --threads 2
```

### Validation Checklist

After running tests, verify:

- [ ] Segments are created in the output directory
- [ ] Each segment is approximately the correct length
- [ ] Video quality is maintained
- [ ] Intro/outro are properly added (if specified)
- [ ] File naming follows the specified pattern
- [ ] No error messages in the logs
- [ ] Original video file is unchanged

## 📊 Performance Testing

For performance testing with real livestream files:

```bash
# Time the splitting process
time stream-splitter long_stream.mp4 -o segments/ -l 20m

# Monitor resource usage
top -p $(pgrep ffmpeg)
```

## 🐛 Reporting Issues

If you encounter problems:

1. Run with verbose logging: `stream-splitter -v ...`
2. Check the log file: `segments/splitter.log`
3. Note your system specifications:
   - OS and version
   - Python version
   - FFmpeg version
   - Input video format and size
   - Error messages

## ✅ Expected Results

After successful testing, you should have:

- ✅ Segments created in output directory
- ✅ Proper file naming and organization
- ✅ Maintained video quality
- ✅ Working intro/outro integration
- ✅ Configuration system functioning
- ✅ Progress tracking and logging
- ✅ Error handling for edge cases

## 🎯 Real-world Testing

For production testing:

1. **Test with actual Kick VODs** of various lengths (30min, 2hr, 4hr+)
2. **Test different video formats** (MP4, MKV, FLV from different sources)
3. **Test with different resolutions** (720p, 1080p, 1440p)
4. **Test with various intro/outro combinations**
5. **Test batch processing** with multiple files
6. **Verify cross-platform compatibility** (Windows, macOS, Linux)

This comprehensive testing ensures the tool works reliably for real-world livestream splitting scenarios!