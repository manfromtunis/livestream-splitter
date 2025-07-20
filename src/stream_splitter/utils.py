"""Utility functions for the livestream splitter"""

import re
import unicodedata
from datetime import timedelta
from pathlib import Path
from typing import Optional


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize a filename to be safe across different operating systems
    
    Args:
        filename: The filename to sanitize
        max_length: Maximum length of the filename
    
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    # Windows invalid characters: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '_', filename)
    
    # Remove Unicode characters that might cause issues
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Replace multiple spaces or underscores with single underscore
    filename = re.sub(r'[\s_]+', '_', filename)
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"
    
    # Truncate to max length
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename


def estimate_file_size(duration: float, bitrate: int) -> int:
    """
    Estimate file size based on duration and bitrate
    
    Args:
        duration: Duration in seconds
        bitrate: Bitrate in bits per second
    
    Returns:
        Estimated file size in bytes
    """
    return int((duration * bitrate) / 8)


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def check_disk_space(path: Path, required_bytes: int) -> bool:
    """
    Check if there's enough disk space
    
    Args:
        path: Path to check disk space for
        required_bytes: Required space in bytes
    
    Returns:
        True if there's enough space, False otherwise
    """
    import shutil
    stat = shutil.disk_usage(path)
    return stat.free > required_bytes


def find_natural_split_points(video_path: Path, target_duration: int) -> list:
    """
    Find natural split points in a video (scene changes, silence)
    This is a placeholder for future implementation
    
    Args:
        video_path: Path to the video file
        target_duration: Target duration for segments
    
    Returns:
        List of timestamps for natural split points
    """
    # TODO: Implement scene detection using OpenCV or similar
    # For now, return empty list to use fixed intervals
    return []


def parse_time_string(time_str: str) -> float:
    """
    Parse time string in various formats to seconds
    
    Supported formats:
    - "120" or "120s" -> 120 seconds
    - "2m" or "2min" -> 120 seconds
    - "1h30m" or "1:30:00" -> 5400 seconds
    
    Args:
        time_str: Time string to parse
    
    Returns:
        Time in seconds
    """
    time_str = time_str.strip().lower()
    
    # Try simple seconds
    if time_str.isdigit():
        return float(time_str)
    
    # Try format with units
    total_seconds = 0
    
    # Hours
    hours_match = re.search(r'(\d+)\s*h', time_str)
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600
    
    # Minutes
    minutes_match = re.search(r'(\d+)\s*m', time_str)
    if minutes_match:
        total_seconds += int(minutes_match.group(1)) * 60
    
    # Seconds
    seconds_match = re.search(r'(\d+)\s*s', time_str)
    if seconds_match:
        total_seconds += int(seconds_match.group(1))
    
    if total_seconds > 0:
        return total_seconds
    
    # Try HH:MM:SS format
    time_parts = time_str.split(':')
    if len(time_parts) == 3:
        try:
            hours, minutes, seconds = map(int, time_parts)
            return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            pass
    
    # Try MM:SS format
    if len(time_parts) == 2:
        try:
            minutes, seconds = map(int, time_parts)
            return minutes * 60 + seconds
        except ValueError:
            pass
    
    raise ValueError(f"Unable to parse time string: {time_str}")


def create_progress_callback(progress_bar):
    """
    Create a progress callback function for FFmpeg
    
    Args:
        progress_bar: tqdm progress bar instance
    
    Returns:
        Callback function
    """
    def callback(progress):
        if progress and 'time' in progress:
            # Update progress based on time processed
            progress_bar.update(1)
    
    return callback