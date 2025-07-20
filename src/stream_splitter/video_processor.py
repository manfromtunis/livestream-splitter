"""FFmpeg-based video processing functionality"""

import ffmpeg
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video processing operations using FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable"""
        import shutil
        
        # Check if ffmpeg is in PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            logger.info(f"Found FFmpeg at: {ffmpeg_path}")
            return 'ffmpeg'
        else:
            logger.warning("FFmpeg not found in PATH")
            return None
    
    def get_video_info(self, input_path: Path) -> Dict:
        """Extract video metadata using ffprobe"""
        try:
            probe = ffmpeg.probe(str(input_path))
            
            # Find the video stream (not audio)
            video_stream = None
            for stream in probe['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                raise ValueError("No video stream found in file")
            
            # Get duration from format if not in video stream
            duration = float(video_stream.get('duration', probe['format']['duration']))
            
            # Parse frame rate safely
            fps_str = video_stream.get('r_frame_rate', '30/1')
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den) if float(den) != 0 else 30.0
            else:
                fps = float(fps_str)
            
            video_info = {
                'duration': duration,
                'width': video_stream['width'],
                'height': video_stream['height'],
                'codec': video_stream['codec_name'],
                'fps': fps,
                'bitrate': int(video_stream.get('bit_rate', 0)),
                'format': probe['format']['format_name']
            }
            return video_info
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise
    
    def split_video(self, 
                   input_path: Path, 
                   output_pattern: str,
                   segment_duration: int,
                   quality_settings: Dict) -> List[Path]:
        """Split video into segments of specified duration"""
        video_info = self.get_video_info(input_path)
        total_duration = video_info['duration']
        num_segments = int(total_duration / segment_duration) + (1 if total_duration % segment_duration > 0 else 0)
        
        output_files = []
        
        for i in range(num_segments):
            start_time = i * segment_duration
            # Replace {index:02d} with the actual segment number
            segment_filename = output_pattern.replace("{index:02d}", f"{i+1:02d}")
            output_path = Path(segment_filename)
            
            # Build FFmpeg command
            stream = ffmpeg.input(str(input_path), ss=start_time, t=segment_duration)
            
            # Apply quality settings
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec=quality_settings.get('codec', 'h264'),
                preset=quality_settings.get('preset', 'medium'),
                crf=quality_settings.get('crf', 23),
                threads=quality_settings.get('threads', 4),
                **{'c:a': 'aac', 'b:a': '192k'}  # Audio settings
            )
            
            # Run FFmpeg command
            try:
                ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
                output_files.append(output_path)
                logger.info(f"Created segment: {output_path}")
            except ffmpeg.Error as e:
                logger.error(f"Error creating segment {i+1}: {e.stderr.decode()}")
                raise
        
        return output_files
    
    def add_intro_outro(self,
                       video_path: Path,
                       intro_path: Optional[Path] = None,
                       outro_path: Optional[Path] = None,
                       output_path: Path = None) -> Path:
        """Add intro and/or outro to a video"""
        if not intro_path and not outro_path:
            # No intro or outro, just return original
            return video_path
        
        if not output_path:
            output_path = video_path.parent / f"processed_{video_path.name}"
        
        # Build concat list
        concat_files = []
        if intro_path and intro_path.exists():
            concat_files.append(intro_path)
        concat_files.append(video_path)
        if outro_path and outro_path.exists():
            concat_files.append(outro_path)
        
        # Create temporary file list for concat
        list_file = video_path.parent / "concat_list.txt"
        with open(list_file, 'w') as f:
            for file in concat_files:
                f.write(f"file '{file.absolute()}'\n")
        
        try:
            # Use concat demuxer
            stream = ffmpeg.input(str(list_file), format='concat', safe=0)
            stream = ffmpeg.output(stream, str(output_path), c='copy')
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
            # Clean up temp file
            list_file.unlink()
            
            logger.info(f"Created video with intro/outro: {output_path}")
            return output_path
        
        except ffmpeg.Error as e:
            logger.error(f"Error adding intro/outro: {e.stderr.decode()}")
            if list_file.exists():
                list_file.unlink()
            raise
    
    def validate_compatibility(self, *video_paths: Path) -> bool:
        """Check if videos have compatible formats for concatenation"""
        if len(video_paths) < 2:
            return True
        
        try:
            infos = [self.get_video_info(path) for path in video_paths if path.exists()]
            
            # Check resolution compatibility
            resolutions = [(info['width'], info['height']) for info in infos]
            if len(set(resolutions)) > 1:
                logger.warning(f"Videos have different resolutions: {resolutions}")
                return False
            
            # Check codec compatibility
            codecs = [info['codec'] for info in infos]
            if len(set(codecs)) > 1:
                logger.warning(f"Videos have different codecs: {codecs}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating compatibility: {e}")
            return False
    
    def create_thumbnail(self, video_path: Path, output_path: Path, time_offset: float = 5.0) -> Path:
        """Extract a thumbnail from the video"""
        try:
            stream = ffmpeg.input(str(video_path), ss=time_offset)
            stream = ffmpeg.output(stream, str(output_path), vframes=1)
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            logger.info(f"Created thumbnail: {output_path}")
            return output_path
        except ffmpeg.Error as e:
            logger.error(f"Error creating thumbnail: {e.stderr.decode()}")
            raise