"""Configuration handling for livestream splitter"""

from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import yaml
import json


class IntroOutroConfig(BaseModel):
    """Configuration for intro and outro videos"""
    intro_path: Optional[Path] = None
    outro_path: Optional[Path] = None

    @validator('intro_path', 'outro_path', pre=True)
    def validate_path(cls, v):
        if v is None:
            return v
        path = Path(v)
        if not path.exists():
            raise ValueError(f"File not found: {path}")
        return path


class OutputConfig(BaseModel):
    """Configuration for output settings"""
    directory: Path = Field(default=Path("./segments"))
    format: str = Field(default="mp4")
    naming_pattern: str = Field(default="{title}_part{index:02d}_{date}")
    max_segment_length: int = Field(default=1200, description="Maximum segment length in seconds")
    
    @validator('directory', pre=True)
    def create_directory(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @validator('max_segment_length')
    def validate_segment_length(cls, v):
        if v < 60:
            raise ValueError("Segment length must be at least 60 seconds")
        if v > 7200:
            raise ValueError("Segment length cannot exceed 2 hours (7200 seconds)")
        return v


class ProcessingConfig(BaseModel):
    """Configuration for video processing"""
    quality: str = Field(default="high", pattern="^(high|medium|low)$")
    codec: str = Field(default="h264")
    threads: int = Field(default=4, ge=1, le=16)
    preset: str = Field(default="medium")  # FFmpeg preset: ultrafast, fast, medium, slow
    crf: int = Field(default=23, ge=0, le=51)  # Constant Rate Factor for quality


class Config(BaseModel):
    """Main configuration class"""
    input_path: Path
    output: OutputConfig = Field(default_factory=OutputConfig)
    intro_outro: IntroOutroConfig = Field(default_factory=IntroOutroConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    
    @validator('input_path', pre=True)
    def validate_input(cls, v):
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Input file not found: {path}")
        if not path.is_file():
            raise ValueError(f"Input path is not a file: {path}")
        
        # Check file extension
        valid_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm', '.ts'}
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        return path

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @classmethod
    def from_json(cls, config_path: Path) -> "Config":
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.model_dump(mode='python')
    
    def save_yaml(self, path: Path) -> None:
        """Save configuration to YAML file"""
        with open(path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
    
    def save_json(self, path: Path) -> None:
        """Save configuration to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)