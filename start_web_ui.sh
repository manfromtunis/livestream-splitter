#!/bin/bash

# Start the Livestream Splitter Web UI

echo "🎬 Starting Livestream Splitter Web UI..."
echo "=" * 40

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg not found. Video processing will fail."
    echo "Install with: sudo apt install ffmpeg"
fi

# Create necessary directories
mkdir -p uploads outputs

# Install additional web dependencies if needed
pip install fastapi uvicorn python-multipart 2>/dev/null

# Start the web server
echo ""
echo "🚀 Starting web server..."
echo "📍 URL: http://localhost:8000"
echo "📋 API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=" * 40

cd web/backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 --limit-max-requests 1000 --timeout-keep-alive 75