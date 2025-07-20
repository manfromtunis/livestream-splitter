# Project Context for Claude

You are working on **Livestream Splitter**, a tool designed for Kick streamers to split long livestream recordings into YouTube-friendly segments.

## Project Overview

This tool helps content creators split their 2-4 hour livestreams into manageable 20-minute segments, perfect for cross-platform distribution. It includes both a CLI and Web UI interface.

**Test Video Available**: `therealbakchich_Just%20Chatting_2025-07-17_720p30.mp4` (2.80 GB, 2h 49m)

## Key Technical Decisions

1. **Python 3.8+** with type hints throughout
2. **FFmpeg** for all video processing operations
3. **Pydantic** for configuration validation
4. **FastAPI** for the web backend
5. **Click** for the CLI framework

## Critical Implementation Details

### Video Processing Gotchas

1. **Stream Detection**: The first stream might be audio, not video. Always find the video stream explicitly:
   ```python
   for stream in probe['streams']:
       if stream['codec_type'] == 'video':
           video_stream = stream
           break
   ```

2. **Frame Rate Parsing**: FFmpeg returns frame rates as fractions (e.g., "30/1"). Parse carefully:
   ```python
   if '/' in fps_str:
       num, den = fps_str.split('/')
       fps = float(num) / float(den)
   ```

3. **String Formatting**: The naming pattern uses `{index:02d}` which conflicts with Python's .format(). Use string replacement:
   ```python
   segment_filename = output_pattern.replace("{index:02d}", f"{i+1:02d}")
   ```

## Development Workflow

### Before Making Changes

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Run regression tests**:
   ```bash
   python test_regression.py
   ```
   All 6 tests must pass.

### After Making Changes

1. **Test with the video file**:
   ```bash
   python -m src.stream_splitter.cli "therealbakchich_Just%20Chatting_2025-07-17_720p30.mp4" --max-length 2m --output-dir test_output
   ```

2. **Run linting** (when available):
   ```bash
   python -m flake8 src/
   python -m mypy src/
   ```

3. **Update session log**:
   - Add entry to `SESSION_LOG.md` with actions taken
   - Document any bugs fixed or features added

## Project Structure

```
.
├── src/stream_splitter/     # Core logic
│   ├── cli.py              # CLI entry point
│   ├── config.py           # Configuration models (Pydantic)
│   ├── splitter.py         # Main splitting orchestration
│   ├── video_processor.py  # FFmpeg operations
│   └── utils.py            # Helper functions
├── web/                    # Web UI
│   ├── backend/main.py     # FastAPI backend
│   └── frontend/           # Static files (HTML/CSS/JS)
├── docs/                   # Documentation
│   └── testing/            # Test results
├── test_regression.py      # Regression test suite
└── SESSION_LOG.md          # Detailed activity log
```

## Configuration Rules

- **Minimum segment length**: 60 seconds (enforced by Pydantic validation)
- **Default segment length**: 20 minutes (1200 seconds)
- **Supported formats**: MP4, MKV, AVI, MOV, FLV, WEBM, TS
- **Output naming pattern**: `{title}_part{index:02d}_{date}`

## Common Commands

```bash
# Process video with default settings (20-minute segments)
python -m src.stream_splitter.cli "video.mp4"

# Custom segment length
python -m src.stream_splitter.cli "video.mp4" --max-length 15m

# With intro/outro
python -m src.stream_splitter.cli "video.mp4" --intro intro.mp4 --outro outro.mp4

# Start web UI
cd web/backend && uvicorn main:app --reload

# Check video info
ffprobe "video.mp4" -v quiet -print_format json -show_streams | grep -A 20 '"codec_type": "video"'
```

## Performance Expectations

- Processing time: ~30-60 seconds per minute of video
- A 3-hour video takes 45-90 minutes to process
- Output size is typically 1.1-1.3x the input size (due to re-encoding)

## Current Status

- ✅ CLI fully functional and tested
- ✅ Web UI frontend and backend created
- ⏳ Web UI integration testing pending
- ⏳ Intro/outro functionality needs testing

## Debugging Tips

1. **"FFmpeg not found"**: Check `which ffmpeg` and ensure it's in PATH
2. **"'width' error"**: The video stream detection failed - check the stream finding logic
3. **"Unknown format code 'd'"**: String formatting issue with the naming pattern
4. **Timeout errors**: Normal for large files - increase timeout or use smaller test segments

## Testing Strategy

Always test changes with:
1. Small segments first (2-5 minutes) for quick validation
2. Then test with default 20-minute segments
3. Finally, verify with the full test video if needed

## Remember

- Keep backward compatibility with the CLI
- Document all changes in SESSION_LOG.md
- Test with real video files, not just unit tests
- The tool is for content creators - prioritize usability and reliability