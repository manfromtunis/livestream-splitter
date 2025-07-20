"""Main splitter logic for processing livestream videos"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from tqdm import tqdm

from .config import Config
from .video_processor import VideoProcessor
from .utils import format_duration, sanitize_filename

logger = logging.getLogger(__name__)


class Splitter:
    """Main class for splitting livestream videos"""
    
    def __init__(self, config: Config):
        self.config = config
        self.video_processor = VideoProcessor()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging"""
        log_file = self.config.output.directory / "splitter.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def process(self) -> List[Path]:
        """Main processing method"""
        logger.info(f"Starting to process: {self.config.input_path}")
        
        # Validate input and intro/outro compatibility
        if not self._validate_inputs():
            raise ValueError("Input validation failed")
        
        # Get video information
        video_info = self.video_processor.get_video_info(self.config.input_path)
        total_duration = video_info['duration']
        
        logger.info(f"Video duration: {format_duration(total_duration)}")
        logger.info(f"Will create segments of max {self.config.output.max_segment_length}s")
        
        # Calculate number of segments
        num_segments = int(total_duration / self.config.output.max_segment_length) + \
                      (1 if total_duration % self.config.output.max_segment_length > 0 else 0)
        
        logger.info(f"Creating {num_segments} segments")
        
        # Generate output pattern
        output_pattern = self._generate_output_pattern()
        
        # Split video into segments
        segment_files = self._split_with_progress(output_pattern, num_segments)
        
        # Add intro/outro if configured
        if self.config.intro_outro.intro_path or self.config.intro_outro.outro_path:
            segment_files = self._add_intro_outro_to_segments(segment_files)
        
        logger.info(f"Processing complete! Created {len(segment_files)} segments")
        return segment_files
    
    def _validate_inputs(self) -> bool:
        """Validate all input files"""
        files_to_check = [self.config.input_path]
        
        if self.config.intro_outro.intro_path:
            files_to_check.append(self.config.intro_outro.intro_path)
        if self.config.intro_outro.outro_path:
            files_to_check.append(self.config.intro_outro.outro_path)
        
        # Check if all files exist
        for file_path in files_to_check:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
        
        # Check compatibility if intro/outro are provided
        if len(files_to_check) > 1:
            if not self.video_processor.validate_compatibility(*files_to_check):
                logger.error("Video files are not compatible for concatenation")
                return False
        
        return True
    
    def _generate_output_pattern(self) -> str:
        """Generate output filename pattern"""
        # Extract base name from input file
        base_name = self.config.input_path.stem
        base_name = sanitize_filename(base_name)
        
        # Get current date
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Build pattern
        pattern = self.config.output.naming_pattern.format(
            title=base_name,
            date=date_str,
            index="{index}"  # This will be filled during splitting
        )
        
        # Add extension
        pattern = str(self.config.output.directory / f"{pattern}.{self.config.output.format}")
        
        return pattern
    
    def _split_with_progress(self, output_pattern: str, num_segments: int) -> List[Path]:
        """Split video with progress bar"""
        segment_files = []
        
        quality_settings = {
            'codec': self.config.processing.codec,
            'preset': self.config.processing.preset,
            'crf': self.config.processing.crf,
            'threads': self.config.processing.threads
        }
        
        with tqdm(total=num_segments, desc="Splitting video", unit="segment") as pbar:
            try:
                segment_files = self.video_processor.split_video(
                    self.config.input_path,
                    output_pattern,
                    self.config.output.max_segment_length,
                    quality_settings
                )
                pbar.update(num_segments)
            except Exception as e:
                logger.error(f"Error during splitting: {e}")
                raise
        
        return segment_files
    
    def _add_intro_outro_to_segments(self, segment_files: List[Path]) -> List[Path]:
        """Add intro and outro to each segment"""
        processed_files = []
        
        with tqdm(total=len(segment_files), desc="Adding intro/outro", unit="file") as pbar:
            for i, segment_file in enumerate(segment_files):
                try:
                    # Generate output filename
                    output_file = segment_file.parent / f"final_{segment_file.name}"
                    
                    # Add intro/outro
                    processed_file = self.video_processor.add_intro_outro(
                        segment_file,
                        self.config.intro_outro.intro_path,
                        self.config.intro_outro.outro_path,
                        output_file
                    )
                    
                    processed_files.append(processed_file)
                    
                    # Remove original segment file to save space
                    segment_file.unlink()
                    
                    pbar.update(1)
                    
                except Exception as e:
                    logger.error(f"Error processing segment {i+1}: {e}")
                    # Keep the original file if processing fails
                    processed_files.append(segment_file)
        
        return processed_files
    
    def generate_report(self, output_files: List[Path]) -> Path:
        """Generate a processing report"""
        report_path = self.config.output.directory / "processing_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("Livestream Splitter - Processing Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Input file: {self.config.input_path}\n")
            f.write(f"Processing date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Number of segments: {len(output_files)}\n")
            f.write(f"Max segment length: {self.config.output.max_segment_length}s\n\n")
            
            if self.config.intro_outro.intro_path:
                f.write(f"Intro: {self.config.intro_outro.intro_path}\n")
            if self.config.intro_outro.outro_path:
                f.write(f"Outro: {self.config.intro_outro.outro_path}\n")
            
            f.write("\nGenerated files:\n")
            for i, file_path in enumerate(output_files, 1):
                f.write(f"{i}. {file_path.name}\n")
        
        logger.info(f"Report generated: {report_path}")
        return report_path