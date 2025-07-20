#!/bin/bash

# Basic usage examples for Livestream Splitter

echo "=== Livestream Splitter - Examples ==="

# Example 1: Basic splitting (20-minute segments)
echo "Example 1: Basic splitting"
echo "stream-splitter my_livestream.mp4"
echo ""

# Example 2: Custom output directory and segment length
echo "Example 2: Custom settings"
echo "stream-splitter my_livestream.mp4 -o youtube_segments/ -l 15m"
echo ""

# Example 3: With intro and outro
echo "Example 3: With intro/outro"
echo "stream-splitter my_livestream.mp4 --intro intro.mp4 --outro outro.mp4"
echo ""

# Example 4: High-quality processing
echo "Example 4: High-quality output"
echo "stream-splitter my_livestream.mp4 --quality high --threads 8 --format mkv"
echo ""

# Example 5: Using configuration file
echo "Example 5: With configuration file"
echo "stream-splitter my_livestream.mp4 -c config/streaming_preset.yaml"
echo ""

# Example 6: Save configuration for reuse
echo "Example 6: Save configuration"
echo "stream-splitter my_livestream.mp4 -l 10m --intro brand_intro.mp4 --save-config my_preset.yaml"
echo ""

echo "Check README.md for more detailed usage instructions!"