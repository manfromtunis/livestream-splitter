"""Tests for configuration handling"""

import pytest
import tempfile
from pathlib import Path
from pydantic import ValidationError

from stream_splitter.config import Config, OutputConfig, IntroOutroConfig, ProcessingConfig


class TestConfig:
    """Test configuration loading and validation"""
    
    def test_default_config(self):
        """Test default configuration values"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(b'fake video data')
            tmp_path = Path(tmp.name)
        
        try:
            config = Config(input_path=tmp_path)
            
            assert config.input_path == tmp_path
            assert config.output.max_segment_length == 1200
            assert config.output.format == "mp4"
            assert config.processing.quality == "high"
        finally:
            tmp_path.unlink()
    
    def test_invalid_input_path(self):
        """Test validation of non-existent input file"""
        with pytest.raises(ValidationError):
            Config(input_path=Path("non_existent_file.mp4"))
    
    def test_invalid_segment_length(self):
        """Test validation of segment length"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(b'fake video data')
            tmp_path = Path(tmp.name)
        
        try:
            # Too short
            with pytest.raises(ValidationError):
                Config(
                    input_path=tmp_path,
                    output=OutputConfig(max_segment_length=30)
                )
            
            # Too long
            with pytest.raises(ValidationError):
                Config(
                    input_path=tmp_path,
                    output=OutputConfig(max_segment_length=8000)
                )
        finally:
            tmp_path.unlink()
    
    def test_yaml_loading(self):
        """Test loading configuration from YAML"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_tmp:
            video_tmp.write(b'fake video data')
            video_path = Path(video_tmp.name)
        
        yaml_content = f"""
input_path: "{video_path}"
output:
  directory: "./test_segments"
  max_segment_length: 900
processing:
  quality: "medium"
  threads: 2
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as yaml_tmp:
            yaml_tmp.write(yaml_content)
            yaml_path = Path(yaml_tmp.name)
        
        try:
            config = Config.from_yaml(yaml_path)
            assert config.input_path == video_path
            assert config.output.max_segment_length == 900
            assert config.processing.quality == "medium"
            assert config.processing.threads == 2
        finally:
            video_path.unlink()
            yaml_path.unlink()


class TestUtils:
    """Test utility functions"""
    
    def test_format_duration(self):
        """Test duration formatting"""
        from stream_splitter.utils import format_duration
        
        assert format_duration(30) == "30s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3661) == "1h 1m 1s"
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        from stream_splitter.utils import sanitize_filename
        
        assert sanitize_filename("test<>file") == "test__file"
        assert sanitize_filename("file with spaces") == "file_with_spaces"
        assert sanitize_filename("") == "unnamed"
    
    def test_parse_time_string(self):
        """Test time string parsing"""
        from stream_splitter.utils import parse_time_string
        
        assert parse_time_string("120") == 120
        assert parse_time_string("2m") == 120
        assert parse_time_string("1h30m") == 5400
        assert parse_time_string("1:30:00") == 5400