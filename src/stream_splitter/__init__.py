"""
Livestream Splitter - Split long livestream recordings into smaller segments
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .splitter import Splitter
from .video_processor import VideoProcessor
from .config import Config

__all__ = ["Splitter", "VideoProcessor", "Config"]