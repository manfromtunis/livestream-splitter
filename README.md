# Livestream Splitter

A powerful tool to split long livestream recordings into digestible segments with customizable intro and outro sequences. Perfect for Kick streamers and content creators who want to repurpose their long-form content for different platforms.

## ✨ Features

- **Automatic Video Splitting**: Split videos into segments with configurable maximum duration (default: 20 minutes)
- **Intro/Outro Integration**: Add custom intro and outro videos to each segment
- **Multiple Format Support**: Works with MP4, MKV, AVI, MOV, FLV, WEBM, and TS files
- **Smart File Naming**: Configurable naming patterns with date and segment numbering
- **Quality Control**: Adjustable output quality and codec settings
- **Progress Tracking**: Real-time progress bars and detailed logging
- **Configuration Files**: Save and reuse processing configurations
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

1. **Install FFmpeg** (required dependency):
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`

2. **Install the tool**:
   ```bash
   pip install -e .
   ```

3. **Verify installation**:
   ```bash
   stream-splitter check-ffmpeg
   ```

### Basic Usage

Split a video into 20-minute segments:
```bash
stream-splitter my_livestream.mp4
```

With custom output directory and segment length:
```bash
stream-splitter my_livestream.mp4 -o segments/ -l 15m
```

Add intro and outro to each segment:
```bash
stream-splitter my_livestream.mp4 --intro intro.mp4 --outro outro.mp4
```

## 📖 Detailed Usage

### Command Line Options

```bash
stream-splitter [OPTIONS] INPUT_FILE

Options:
  -o, --output-dir PATH       Output directory for segments [default: ./segments]
  -l, --max-length TEXT       Maximum segment length (e.g., 20m, 1200s, 1h30m) [default: 20m]
  --intro PATH               Path to intro video file
  --outro PATH               Path to outro video file
  -f, --format [mp4|mkv|avi|mov]  Output format for segments [default: mp4]
  --naming-pattern TEXT      Naming pattern for output files [default: {title}_part{index:02d}_{date}]
  --quality [high|medium|low] Output quality preset [default: high]
  --threads INTEGER          Number of threads for processing [default: 4]
  -c, --config PATH          Configuration file (YAML or JSON)
  --save-config PATH         Save current configuration to file
  -v, --verbose              Enable verbose logging
  --help                     Show this message and exit.
```

### Time Format Examples

The `--max-length` option accepts various time formats:

- `20m` or `20min` → 20 minutes
- `1200` or `1200s` → 1200 seconds
- `1h30m` → 1 hour 30 minutes
- `1:30:00` → 1 hour 30 minutes (HH:MM:SS)
- `90:00` → 90 minutes (MM:SS)

### Configuration Files

Create a configuration file to save your settings:

```yaml
# config.yaml
input_path: "my_livestream.mp4"
output:
  directory: "./segments"
  format: "mp4"
  naming_pattern: "{title}_segment{index:02d}_{date}"
  max_segment_length: 1200  # 20 minutes

intro_outro:
  intro_path: "intro.mp4"
  outro_path: "outro.mp4"

processing:
  quality: "high"
  codec: "h264"
  preset: "medium"
  threads: 4
```

Use the configuration file:
```bash
stream-splitter -c config.yaml my_livestream.mp4
```

Save current settings to a config file:
```bash
stream-splitter my_livestream.mp4 -l 15m --intro intro.mp4 --save-config my_settings.yaml
```

## 🎯 Use Cases

### Content Creator Workflow

1. **Stream on Kick**: Create long-form content (2-4 hours)
2. **Download VOD**: Use third-party tools to download the recording
3. **Split Content**: Use this tool to create 20-minute segments
4. **Cross-Platform**: Upload segments to YouTube, TikTok, or other platforms

### Example Commands

**Basic splitting for YouTube uploads**:
```bash
stream-splitter "My Gaming Stream 2024-01-15.mp4" -o youtube_segments/ -l 20m
```

**With branded intro/outro for professional content**:
```bash
stream-splitter stream.mp4 \
  --intro channel_intro.mp4 \
  --outro subscribe_outro.mp4 \
  --naming-pattern "Stream_{date}_Part{index:02d}" \
  -o branded_content/
```

**High-quality processing for archival**:
```bash
stream-splitter stream.mp4 \
  --quality high \
  --format mkv \
  --threads 8 \
  -o archive/
```

## 🔧 Advanced Features

### File Naming Patterns

Customize output filenames using these variables:

- `{title}`: Original filename (sanitized)
- `{index}`: Segment number (use `:02d` for zero-padding)
- `{date}`: Current date (YYYYMMDD format)

Examples:
- `{title}_part{index:02d}_{date}` → `stream_part01_20240115`
- `Segment{index:03d}_{title}` → `Segment001_my_stream`
- `{date}_{title}_{index}` → `20240115_stream_1`

### Quality Settings

- **High**: Best quality, larger file sizes (CRF 18-23)
- **Medium**: Balanced quality and size (CRF 23-28)
- **Low**: Smaller files, lower quality (CRF 28-35)

### Processing Optimization

- Use more threads (`--threads 8`) for faster processing on multi-core systems
- Choose appropriate presets: `ultrafast`, `fast`, `medium`, `slow`
- Monitor disk space - output can be 1.5-2x the input size

## 🛠️ Development

### Project Structure

```
livestream-splitter/
├── src/stream_splitter/     # Main package
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration handling
│   ├── splitter.py         # Main splitting logic
│   ├── video_processor.py  # FFmpeg operations
│   └── utils.py            # Helper functions
├── tests/                  # Test suite
├── web/                    # Web UI (future)
├── config/                 # Default configurations
└── examples/               # Usage examples
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

### Building from Source

```bash
git clone <repository-url>
cd livestream-splitter
pip install -e .
```

## 🐛 Troubleshooting

### Common Issues

**"FFmpeg not found"**
- Ensure FFmpeg is installed and in your PATH
- Run `stream-splitter check-ffmpeg` to verify

**"Memory error with large files"**
- Reduce thread count (`--threads 2`)
- Process smaller segments first
- Ensure sufficient RAM (8GB+ recommended for 4K videos)

**"Incompatible video formats"**
- Convert intro/outro to match main video format
- Use same resolution and codec for all inputs

**"Permission denied errors"**
- Check write permissions to output directory
- Run with administrator privileges if needed

### Getting Help

- Check the logs in `segments/splitter.log`
- Use `--verbose` flag for detailed output
- Report issues on GitHub

## 📋 Requirements

- **Python**: 3.8 or higher
- **FFmpeg**: Latest stable version
- **Disk Space**: 2-3x the input file size for processing
- **RAM**: 4GB minimum, 8GB+ recommended for large files

## 🚀 Future Features

- **Web UI**: Browser-based configuration interface
- **Batch Processing**: Process multiple files simultaneously
- **Smart Splitting**: Scene detection and natural break points
- **Direct Integration**: Download directly from Kick when API supports it
- **Cloud Processing**: Optional cloud-based processing
- **AI Highlights**: Automatic detection of engaging moments

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⭐ Support

If this tool helps you create better content, consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features
- 📖 Improving documentation

---

**Made for Kick streamers, by content creators** 🎮✨